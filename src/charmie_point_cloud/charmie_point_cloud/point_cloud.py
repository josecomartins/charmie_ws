#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String, Float32
from charmie_interfaces.msg import NeckPosition, RequestPointCloud, RetrievePointCloud
from geometry_msgs.msg import Point, Pose2D
from cv_bridge import CvBridge, CvBridgeError

import numpy as np
import cv2
import math
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
import time



# x do robô para a frente
# y da direita para a esquerda
# z de baixo para cima


DEBUG_DRAW = True

GRAF3D = True
GRAF1 = False
GRAF2 = True

x1 = -1     # coordenadas do rato
y1 = -1     # coordenadas do rato
WIDTH = 100 # largura da Bounding box
HEIGHT = 100 # altura da Bounding box

# maximum and minimum distnace considered, outside this range is 0
MAX_DIST = 6000
MIN_DIST = 300

linhas = 720
colunas = 1280

Z_MIN_A_VER = -1100
inc = 5

ELEV = -150
AZIM = -35
DIM = 6000

# according to the kinematics at the moment, the origin is the actuation of the pan servo, therefore to consider the same (x, y, z) as the robot localisation
# we must shift the axis so the new origin is the center of the robot on the floor
Z_SHIFT = (1245+160) # height of the servos from the floor + height from the servos to the camera (altura pescoco+ dist. pescoço-camara

flag_show_rgb_depth = True

nome = "Image Debug"


# Create a named window
cv2.namedWindow(nome)



class PointCloud():
    def __init__(self):
        print("New PointCloud Class Initialised")

        global linhas, colunas, nome
        # print(linhas, colunas)
        
        # Parametros intrinsecos da Camera (Dados pelo Tiago por email)
        self.fx = 633.811950683593  # Distancia Focal em pixels (x-direction)
        self.fy = 633.234680175781  # Distancia Focal em pixels (y-direction)
        self.cx = 629.688598632812  # Ponto Principal em pixels (x-coordinate)
        self.cy = 393.705749511718  # Ponto Principal em pixels (y-coordinate)

        # cinematica do cabeça do robo
        self.DOF = 3
        self.teta = [  0,   0,   0]
        self.alfa = [ 90, -90,   0]
        self.d =    [ 25,   0, 145]
        self.l =    [ 28,   0, 130]

        # estes 4 não deviam ter uma variavel???????????
        # self.T=np.identity(4)
        self.inverse_matrix = np.zeros([4, 4]) 
        # print(self.inverse_matrix)

        # self.Z_MIN_A_VER = -1100
        # self.inc = 5

        self.rgb_img_pc = np.zeros((linhas,colunas,3), dtype=np.uint8)
        self.depth_img_pc = np.zeros((linhas,colunas), dtype=np.uint8)

        # self.points = []  # Inicializa um array vazio para os points
        # self.lista_points = []   # [u,v] [linha, coluna]  [cima-baixo, esquerda-direita]
        # self.FINAL1 = []
        # self.FINAL2 = []
        # self.FINAL3 = []
        self.ESCALA = 16  # Por questões de eficiencia, só vamos considerar 1 pixel em cada 4

        # self.retrieve_bbox = False

        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.RECEBO = []
        self.ENVIO = []

        if GRAF3D:
            if GRAF1:
                # inicializações necessárias para desenhar graficos com o MatPlotLib
                self.fig = plt.figure()
                # fig_manager = plt.get_current_fig_manager()
                # fig_manager.full_screen_toggle()           # para maximizar a janela do grafico 3D
                # fig_manager.window.wm_geometry(f"+{50}+{50}")
                
                #fig_manager = plt.get_current_fig_manager()
                #fig_manager.full_screen_toggle()
                plt.ion()  # Enable interactive mode
                self.ax1 = self.fig.add_subplot(221)
                self.ax2 = self.fig.add_subplot(222)
                self.ax3 = self.fig.add_subplot(223)
                self.ax4 = self.fig.add_subplot(224, projection='3d')
                self.ax4.mouse_init()

            if GRAF2:
                self.fig2 = plt.figure()
                self.ax5 = self.fig2.add_subplot(111, projection='3d')
                self.ax5.mouse_init()


        self.actualiza_tetas(' ')
        self.robo()      # calcula a cinematica uma vez para os inverse_matrix ter valores
        self.converter_2D_3D(0, 0, linhas, colunas)

        if GRAF3D == 1:
            self.graficos()

    
    def click_event(self, event, x, y, flags, param):
        global x1, y1, nova, flag_show_rgb_depth    #, WIDTH, HEIGHT
        if event == cv2.EVENT_LBUTTONDOWN:
            x1=x
            y1=y
            flag_show_rgb_depth = True
            '''
            # retirei esta opção porque agora as janelas já estão definidas por variável
            nova = jpg.copy()       # quando clico no rato devo mostrar o rectangulo da bounding box
            cv2.rectangle(nova, (x1, y1), (x1+WIDTH, y1+HEIGHT), 255, 2)
            cv2.imshow(nome, nova)
            '''
        if event == cv2.EVENT_MBUTTONDOWN:          # MOSTRA a janela DEPTH
            # cv2.imshow(nome, self.depth_img_pc)
            flag_show_rgb_depth = False
        if event == cv2.EVENT_MOUSEMOVE:            # MOSTRA as coordenadas 3D por cima da janela RGB
            
            x1=x
            y1=y
            # self.update_imagem()
            coordx, coordy, coordz = self.converter_2D_3D_unico(y, x)
            cv2.rectangle(nova, (0,0), (280, 60), (0, 0, 0), -1)
            texto = "{}, {}, {}".format(int(coordx)/1000, int(coordy)/1000, int(coordz)/1000)
            cv2.putText(nova, texto, (10, 25), self.font, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
            texto = "( {}, {} )".format(x, y)
            cv2.putText(nova, texto, (65, 50), self.font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            # cv2.imshow(nome, nova)
            
            
            
            if flag_show_rgb_depth:
                self.update_imagem()
            else:
                t_ = self.depth_img_pc.copy()
                _, maximo, _, _= cv2.minMaxLoc(t_)
                t_ = t_ / maximo * 255 
                t_ = t_.astype(np.uint8)
                cv2.imshow(nome, t_)
            
            

    def Trans(self, tx, ty, tz):
        M = np.identity(4)
        M[0][3] = tx
        M[1][3] = ty
        M[2][3] = tz
        return M

    def Rot(self, eixo, angulo):
        ang_rad = angulo*math.pi/180.0
        c = math.cos(ang_rad)
        s = math.sin(ang_rad)
        M = np.identity(4)
        if (eixo == 'x' or eixo == 'X'):
            M[1][1] = M[2][2] = c
            M[1][2] = -s
            M[2][1] = s
        elif (eixo == 'y' or eixo == 'Y'):
            M[0][0] = M[2][2] = c
            M[0][2] = s
            M[2][0] = -s
        elif (eixo == 'z' or eixo == 'Z'):
            M[0][0] = M[1][1] = c
            M[0][1] = -s
            M[1][0] = s
        return M

    def braco(self, talfa, tteta, td, tl):
        a=self.Rot('z', tteta)
        b=self.Trans(tl, 0, td)
        c=self.Rot('x', talfa)
        temp = np.dot(a,b)
        T = np.dot(temp,c)
        return T
    
    def robo(self):
        T=np.identity(4)
        for i in range(self.DOF):
            T=np.dot(T,self.braco(self.alfa[i], self.teta[i], self.d[i], self.l[i]))
        self.inverse_matrix = np.linalg.inv(T)
        # return self.inverse_matrix

    def actualiza_tetas(self, tecla):
        global ELEV, AZIM, inc, DIM, Z_MIN_A_VER, WIDTH, HEIGHT, x1, y1

        if tecla==ord('1'):
            self.teta[0] = self.teta[0] +inc
        elif tecla==ord('2'):
            self.teta[1] = self.teta[1] +inc

        elif tecla==ord('q'):
            self.teta[0] = self.teta[0] -inc
        elif tecla==ord('w'):
            self.teta[1] = self.teta[1] -inc

        elif tecla == ord('a'):
            ELEV = ELEV + inc
        elif tecla == ord('z'):
            ELEV = ELEV - inc

        elif tecla == ord('I'):
            inc = inc + 1
        elif tecla == ord('i'):
            inc = inc - 1

        elif tecla == ord('c'):
            AZIM = AZIM - inc
        elif tecla == ord('x'):
            AZIM = AZIM + inc

        elif tecla == ord('+'):
            DIM = DIM + 200
        elif tecla == ord('-'):
            DIM = DIM - 200

        elif tecla == ord('n'):
            Z_MIN_A_VER = Z_MIN_A_VER + 100
        elif tecla == ord('m'):
            Z_MIN_A_VER = Z_MIN_A_VER - 100

        elif tecla == ord('7'):
            WIDTH = WIDTH - 10
        elif tecla == ord('8'):
            WIDTH = WIDTH + 10
        elif tecla == ord('9'):
            HEIGHT = HEIGHT - 10
        elif tecla == ord('0'):
            HEIGHT = HEIGHT + 10

        elif tecla == ord('S'):
            self.ESCALA = self.ESCALA + 1
        elif tecla == ord('s'):
            self.ESCALA = self.ESCALA - 1

        elif tecla == ord('p'):
            HEIGHT = 500
            WIDTH = 1000
            x1 = 100
            y1 = 100

        elif tecla==ord('.'):
            for i in range(self.DOF):
                self.teta[i] = 0

        # self.show_images()


    # def show_images(self):
        # quando pressionar uma tecla qualquer, redesenha tudo para actualizar as variáveis
        # nova = self.jpg.copy()
        # cv2.rectangle(self.rgb_img_pc, (x1, y1), (x1+WIDTH, y1+HEIGHT), 255, 2)
        # cv2.imshow("New Image", self.rgb_img_pc)
        # cv2.imshow("Depth Image", self.depth_img_pc)
        # print("RGB:", self.rgb_img_pc.shape, "DEPTH:", self.depth_img_pc.shape)
        # cv2.waitKey(1)
        # pass

    def converter_2D_3D_unico(self, u, v):
        # global txt, cx, cy, fx, fy

        # depth = txt[u][v]
        depth = self.depth_img_pc[u][v]
        if depth == 0:      # Só faz os cálculos de o ponto for válido (OPTIMIZAÇÃO)

            # casos especiais, mas só em coordenadas especificas (não faz para a bounding box toda)
            # procuro a distancia mais próxima nos pixeis vizinhos
            raio = 1
            while np.all(self.depth_img_pc[u - raio:u + raio + 1, v - raio:v + raio + 1] == 0):
                raio += 1
            nao_zeros = (self.depth_img_pc[u - raio:u + raio + 1, v - raio:v + raio + 1] != 0)
            depth = np.min(self.depth_img_pc[u - raio:u + raio + 1, v - raio:v + raio + 1][nao_zeros])
            #print('u, v, min ', u, v, depth)
            #result = [0, 0, 0]
        #else:
        Z = depth
        X = (v - self.cx) * depth / self.fx
        Y = (u - self.cy) * depth / self.fy

        xn = Z
        yn = -X
        zn = -Y
        result = np.dot(self.inverse_matrix, [xn, yn, zn, 1])
        # result[0] += correcao no eixo dos xx
        result[2] += Z_SHIFT  # Z=0 passa a ser o chão do laboratorio
        result = result[0:3].astype(np.int16)
        result = result.tolist()
        return result

    
    def converter_2D_3D(self, u, v, height, width):
        
        # self.points = []  # Initialize an empty list for storing points
        # self.FINAL1 = []
        # self.FINAL2 = []
        # self.FINAL3 = []

        points = []

        # print(self.inverse_matrix)
        # calcula toda a bounding box        
        # if self.retrieve_bbox: # ver no futuro se faz sentido
        for u1 in range(u, u+height, self.ESCALA):
            for v1 in range(v, v+width, self.ESCALA):
                depth = self.depth_img_pc[u1][v1]
                if depth == 0:      # Só faz os cálculos se o ponto for válido (OPTIMIZAÇÃO)
                    result = [0,0,0]
                else:
                    X = (v1 - self.cx) * depth / self.fx
                    Y = (u1 - self.cy) * depth / self.fy
                    Z = depth

                    xn = Z
                    yn = -X
                    zn = -Y
                    result = np.dot(self.inverse_matrix, [xn, yn, zn, 1])
                    # result[0] += correcao no eixo dos xx
                    result[2] += Z_SHIFT  # Z=0 passa a ser o chão do laboratorio 

                    result = result[0:3].astype(np.int16)
                    result = result.tolist()

                points.append(result)
        return points
    
    
    """               
                # print(u1, v1, depth)
                X = (v1 - self.cx) * depth / self.fx
                Y = (u1 - self.cy) * depth / self.fy
                Z = depth

                xn = Z
                yn = -X
                zn = -Y
                # CONFIRMAR INVERSE MATRIXX É MESMO T
                result = np.dot(self.inverse_matrix, [xn, yn, zn, 1])
                # print(".")
                #if result[2]>Z_MIN_A_VER:  # Para limpar os pontos do chão
                self.points.append([result[0], result[1], result[2]])
                self.FINAL3.append([result[0], result[1], result[2]])
        #print('FINAL3=', FINAL3)

        # calcula o ponto central da bounding box
        coord = self.especifico(height/ 2, width/2, height, width)
        self.FINAL1 = coord
        print('FINAL1=', self.FINAL1)

        # DEPOIS TEM QUE SE APAGAR ISTO
        # calcula uma lista de pontos
        # self.lista_points = []

        print("lp:", self.lista_points)

        nova = self.rgb_img_pc.copy()

        for i in range(len(self.lista_points)):
            # cv2.circle(nova, (self.lista_points[i][1], self.lista_points[i][0]), 3, (255,255,255), 1)
            coord = self.especifico(self.lista_points[i][0]-u, self.lista_points[i][1]-v, height, width)
            self.FINAL2.append(coord)
        cv2.imshow("DEBUG DRAWINGS", nova)
        print('FINAL2=', self.FINAL2)

        self.points = np.array(self.points)  # Convert the list of points to a numpy array para desenhar os graficos a 3D
    """

    def graficos(self):

        global DIM
        
        CUBO = 1
        RETA = 0      # dimensão das eixos que vou desenhar

        #print(self.points)
        #print(self.points[:,2])

        if self.ENVIO: # Se houver dados para representar

            points = self.ENVIO[0][2].copy()
            for i in range(1,len(self.ENVIO)):
                points = np.concatenate([points, self.ENVIO[i][2]])

            if GRAF1:

                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                self.ax4.clear()

                # Y-X Plane (TOP View)
                norm = Normalize(vmin=min(points[:,2]), vmax=max(points[:,2]))
                colors = norm(points[:,2])  # Map z values to the [0, 1] range using the Normalize object
                #points = points[points[:, 2].argsort()[::-1]]
                self.ax1.scatter(points[:, 1], points[:, 0], marker='.', c=colors, cmap='hsv')
                self.ax1.set_xlabel('Y')
                self.ax1.set_ylabel('X')
                self.ax1.set_title('Y-X Plane - TOP view')
                #ax1.set_ylim(max(points[:, 1]), min(points[:, 1]))
                self.ax1.set_xlim( DIM,-DIM)
                self.ax1.set_ylim(0, DIM)
                self.ax1.set_aspect('equal')

                # X-Z Plane (right SIDE View)
                norm = Normalize(vmin=min(points[:,1]), vmax=max(points[:,1]))
                colors = norm(points[:,1])  # Map z values to the [0, 1] range using the Normalize object
                #points = points[points[:, 1].argsort()]
                self.ax2.scatter(points[:, 0], points[:, 2], marker='.', c=colors, cmap='hsv')
                self.ax2.set_xlabel('X')
                self.ax2.set_ylabel('Z')
                self.ax2.set_title('X-Z Plane - SIDE view')
                self.ax2.set_xlim(0, DIM)
                self.ax2.set_ylim(-DIM//2, DIM//2)
                self.ax2.set_aspect('equal')

                # Z-Y Plane (FRONT View)
                norm = Normalize(vmin=min(points[:,2]), vmax=max(points[:,2]))
                colors = norm(points[:,2])  # Map z values to the [0, 1] range using the Normalize object
                self.ax3.scatter(points[:, 1], points[:, 2], marker='.', c=colors, cmap='hsv')
                self.ax3.set_xlabel('Y')
                self.ax3.set_ylabel('Z')
                self.ax3.set_title('Y-Z Plane - FRONT view')
                self.ax3.set_xlim( DIM, -DIM)
                self.ax3.set_ylim(-DIM//2,  DIM//2)
                self.ax3.set_aspect('equal')

                # jet rainbow, hsv brg
                norm = Normalize(vmin=min(points[:,2]), vmax=max(points[:,2]))
                colors = norm(points[:,2])  # Map z values to the [0, 1] range using the Normalize object

                # 3D Orthogonal View
                self.ax4.scatter(points[:, 0], points[:, 1], points[:, 2], marker='.', c=colors, cmap='hsv')
                self.ax4.set_xlabel('X')
                self.ax4.set_ylabel('Y')
                self.ax4.set_zlabel('Z')
                self.ax4.set_title('Orthogonal')
                self.ax4.set_xlim(0,  DIM)
                self.ax4.set_ylim( DIM, -DIM)
                self.ax4.set_zlim( DIM//2, -DIM//2)
                #ax4.set_xlim(    0, 3000)
                #ax4.set_ylim(3000,     0)
                #ax4.set_zlim(2000, -2000)
                self.ax4.set_aspect('equal')
                self.ax4.view_init(elev=ELEV, azim=AZIM)

            if GRAF2:

                self.ax5.clear()

                # junto os pontos todos das N Bounding Boxes (OPTIMIZAÇÃO)
                # points = self.ENVIO[0][2].copy()
                # for i in range(1,len(self.ENVIO)):
                #     points = np.concatenate([points, self.ENVIO[i][2]])

                norm = Normalize(vmin=min(points[:,2]), vmax=max(points[:,2]))
                colors = norm(points[:,2])  # Map z values to the [0, 1] range using the Normalize object

                # 3D Orthogonal View
                self.ax5.scatter(points[:, 0], points[:, 1], points[:, 2], marker='.', c=colors, cmap='hsv')
                

                for i in range(len(self.RECEBO)):
                    if CUBO == 1:
                        points = np.array(self.ENVIO[i][2])

                        print(points)

                        filtered_points = points[points[:, 2] != 0]
                        px = filtered_points[:, 0]
                        py = filtered_points[:, 1]
                        pz = filtered_points[:, 2]

                        # Define os 8 vertices do cuboide
                        minx = np.amin(px)
                        maxx = np.amax(px)
                        miny = np.amin(py)
                        maxy = np.amax(py)
                        minz = np.amin(pz)
                        maxz = np.amax(pz)
                        vertices = [
                            [minx, miny, minz],
                            [maxx, miny, minz],
                            [maxx, maxy, minz],
                            [minx, maxy, minz],
                            [minx, miny, maxz],
                            [maxx, miny, maxz],
                            [maxx, maxy, maxz],
                            [minx, maxy, maxz]
                        ]
                        # Define as 12 linhas do cuboide
                        lines = [
                            [vertices[0], vertices[1]],
                            [vertices[1], vertices[2]],
                            [vertices[2], vertices[3]],
                            [vertices[3], vertices[0]],
                            [vertices[4], vertices[5]],
                            [vertices[5], vertices[6]],
                            [vertices[6], vertices[7]],
                            [vertices[7], vertices[4]],
                            [vertices[0], vertices[4]],
                            [vertices[1], vertices[5]],
                            [vertices[2], vertices[6]],
                            [vertices[3], vertices[7]]
                        ]
                        # Desenhas as linhas do cuboide
                        for line in lines:
                            x, y, z = zip(*line)
                            self.ax5.plot(x, y, z, c='black', label='Centro')

                    if RETA != 0:
                        res = self.ENVIO[i]
                        bbox = self.RECEBO[i] #### ??????????????????????????????????????????????????? ELE ESQUECEU-SE ....
                        

                        # desenha EIXOS do ponto central da bounding box
                        if any(num != 0 for num in res[0]):     # se a coordenada for [0, 0, 0] não desenha eixos - QUEREMOS ???
                            coordx, coordy, coordz = res[0]
                            lines = [
                                [[coordx - RETA, coordy, coordz], [coordx + RETA, coordy, coordz]],
                                [[coordx, coordy - RETA, coordz], [coordx, coordy + RETA, coordz]],
                                [[coordx, coordy, coordz - RETA], [coordx, coordy, coordz + RETA]]
                            ]
                            for line in lines:
                                x, y, z = zip(*line)
                                self.ax5.plot(x, y, z, c='red', label='Outros')

                        # desenha EIXOS dos pontos da lista da bounding box
                        for j in range(len(bbox[1])):
                            # bb = bbox[1][j]
                            out = res[1][j]
                            if any(num != 0 for num in out):  # se a coordenada for [0, 0, 0] não imprime
                                coordx, coordy, coordz = out
                                lines = [
                                    [[coordx-RETA, coordy, coordz], [coordx+RETA, coordy, coordz]],
                                    [[coordx, coordy-RETA, coordz], [coordx, coordy+RETA, coordz]],
                                    [[coordx, coordy, coordz-RETA], [coordx, coordy, coordz+RETA]]
                                ]
                                for line in lines:
                                    x, y, z = zip(*line)
                                    self.ax5.plot(x, y, z, c='blue', label='especificos')

                self.ax5.set_xlabel('X')
                self.ax5.set_ylabel('Y')
                self.ax5.set_zlabel('Z')
                self.ax5.set_xlim(   0,  DIM)
                self.ax5.set_ylim( DIM, -DIM)
                self.ax5.set_zlim( DIM,    0)
                self.ax5.set_aspect('equal')
                self.ax5.view_init(elev=ELEV, azim=AZIM)

            plt.pause(0.1)


    def update_imagem(self):
        global nova, nome

        if self.ENVIO:       # garantir que a lista não está vazia
            nova = self.rgb_img_pc
            for i in range(len(self.RECEBO)):
                bbox = self.RECEBO[i]
                res = self.ENVIO[i]
                u_inicial, v_inicial, HEIGHT, WIDTH = bbox[0]
                cv2.rectangle(nova, (v_inicial, u_inicial), (v_inicial + WIDTH, u_inicial + HEIGHT), (255, 0, 0), 2)
                cv2.circle(nova, (v_inicial + WIDTH // 2, u_inicial + HEIGHT // 2), 3, (0, 0, 255), 2)
                str_central = "{}, {}, {}".format(int(res[0][0])/1000, int(res[0][1])/1000, int(res[0][2])/1000)
                cv2.putText(nova, str_central, (v_inicial + WIDTH // 2 + 20, u_inicial + HEIGHT // 2 + 6), self.font, 0.5, (0, 0, 255), 1,
                            cv2.LINE_AA)
                for j in range(len(bbox[1])):
                    bb = bbox[1][j]
                    out = res[1][j]
                    cv2.circle(nova, (bb[1], bb[0]), 3, (255, 0, 0), 2)
                    str_temp = "{}, {}, {}".format(out[0]/1000, out[1]/1000, out[2]/1000)
                    cv2.putText(nova, str_temp, (bb[1] + 20, bb[0] + 6), self.font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
            

        coordx, coordy, coordz = self.converter_2D_3D_unico(y1, x1)
        cv2.rectangle(nova, (0,0), (280, 60), (0, 0, 0), -1)
        texto = "{}, {}, {}".format(int(coordx)/1000, int(coordy)/1000, int(coordz)/1000)
        cv2.putText(nova, texto, (10, 25), self.font, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
        texto = "( {}, {} )".format(x1, y1)
        cv2.putText(nova, texto, (65, 50), self.font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(nome, nova)





class PointCloudNode(Node):

    def __init__(self):
        super().__init__("PointCloud")
        self.get_logger().info("Initialised CHARMIE PointCloud Node")
        
        # Intel Realsense Subscribers
        self.color_image_subscriber = self.create_subscription(Image, "/color/image_raw", self.get_color_image_callback, 10)
        self.aligned_depth_image_subscriber = self.create_subscription(Image, "/aligned_depth_to_color/image_raw", self.get_aligned_depth_image_callback, 10)
        
        # Neck Position
        self.neck_get_position_subscriber = self.create_subscription(NeckPosition, "get_neck_pos", self.get_neck_position_callback, 10)

        # RequestPointCloud
        self.request_point_cloud_subscriber = self.create_subscription(RequestPointCloud, "ask_point_cloud", self.get_request_point_cloud_callback, 10)

        # RetrievePointCloud
        self.retrieve_point_cloud_publisher = self.create_publisher(RetrievePointCloud, "get_point_cloud", 10)

        # self.create_timer(0.01, self.get_request_point_cloud_callback)

        # Point Cloud Instance
        self.br = CvBridge()
        self.rgb_img = Image()
        self.depth_img = Image()
        self.neck_position = NeckPosition()
        self.pcloud = PointCloud()



        lb=cv2.setMouseCallback(nome, self.pcloud.click_event)      # inicializa a rotina do rato

        
        self.tempo_calculo = 0
        self.tempo_frame = 0

    def get_color_image_callback(self, img: Image):
        self.rgb_img = img
        # print("Received RGB Image")

    def get_aligned_depth_image_callback(self, img: Image):
        self.depth_img = img
        # print("Received Depth Image")

    def get_neck_position_callback(self, neck_pos: NeckPosition):
        self.neck_position = neck_pos
        self.pcloud.teta[0] = 180 - neck_pos.pan
        self.pcloud.teta[1] = 190 - neck_pos.tilt ###### ALTERAR PARA 180
        print("Received Neck Position: (", neck_pos.pan, ",", neck_pos.tilt, ") - (", self.pcloud.teta[1], ",", self.pcloud.teta[2], ")")

    def get_request_point_cloud_callback(self, req: RequestPointCloud): #, req: RequestPointCloud):

        global WIDTH, HEIGHT, flag_show_rgb_depth
        
        if self.depth_img.height > 0 and self.rgb_img.height > 0: # prevents doing this code before receiving images

            rgb_frame = self.br.imgmsg_to_cv2(self.rgb_img, "bgr8")
            depth_frame = self.br.imgmsg_to_cv2(self.depth_img, desired_encoding="passthrough")
            
            width = self.rgb_img.width
            height = self.rgb_img.height

            depth_frame_res = cv2.resize(depth_frame, (width, height), interpolation = cv2.INTER_NEAREST)

            depth_frame_res[depth_frame_res > MAX_DIST] = 0
            depth_frame_res[depth_frame_res < MIN_DIST] = 0

            self.pcloud.rgb_img_pc = rgb_frame
            self.pcloud.depth_img_pc = depth_frame_res
        
            """
            self.pcloud.lista_points = []
            for i in range(len(req.requested_point_coords)):
                # p = Pose2D()
                # p = req.
                self.pcloud.lista_points.append([req.requested_point_coords[i].y, req.requested_point_coords[i].x])   # [u,v] [linha, coluna]  [cima-baixo, esquerda-direita]

            print(self.pcloud.lista_points)
            self.pcloud.retrieve_bbox = req.retrieve_bbox 

            """
            tecla = cv2.waitKey(1)  # le uma tecla
            if tecla != 27:         # se não for a tecla de ESCAPE, faz todo o processamento
                self.pcloud.actualiza_tetas(tecla)  # actualiza as variaveis Theta da cinematica
            # else:
                # self.pcloud.show_images()
            
            #  T = self.pcloud.robo()              # calcula a matris inversa da cabeça toda
           

            # imprime as variaveis todas apenas para DEBUG no terminal
            print("[ ", end=' ')
            for i in self.pcloud.teta[0:2]:
                print("{:>3.0f}".format(i), end=' ')
            print("]  -> ", end=' ')
            '''
            for i in T[0:3, 3]:
                print("{:>8.3f}".format(i), end=' ')
            '''
            print('inc=', inc, '  ELEV=', ELEV, '  AZIM=', AZIM, ' DIM=', DIM, ' Z_MIN_A_VER=', Z_MIN_A_VER, ' WIDTH=', WIDTH, ' HEIGHT=', HEIGHT, ' ESCALA=', self.pcloud.ESCALA)
            print("tetas = ", self.pcloud.teta)
            
            # REMOVER! -  ????????????????????????????????????????????????
            self.pcloud.RECEBO = [
                [
                    # bounding box 1
                    [367, 324, 120, 130],   # U, V, Height, Width
                    [[367 + 25, 324 + 75], [367 + 75, 324 + 25], [367 + 75, 324 + 75]]  # Pontos especificos
                ],
                [
                    # bounding box 2
                    [81, 624, 230, 110],
                    [[81 + 25, 624 + 75], [81 + 75, 624 + 25], [81 + 75, 624 + 75]]
                ],
                [
                    # bounding box 3
                    [350, 930, 240, 280],
                    [[350 + 25, 930 + 75], [350 + 75, 930 + 25], [350 + 75, 930 + 75]]
                ]
            ]

            
            self.pcloud.ENVIO = []      # limpo a variavel onde vou guardar as minhas respostas, para este novo ciclo
            self.tempo_calculo = time.perf_counter()

            # calculo dos vários Bounding Boxes
            self.pcloud.robo()              # calcula a matris inversa da cabeça toda
            for bbox in self.pcloud.RECEBO:

                # le os dados da BouundingBox
                u_inicial, v_inicial, HEIGHT, WIDTH = bbox[0]

                # calcula o ponto do centro
                resp_centro = self.pcloud.converter_2D_3D_unico(u_inicial + HEIGHT//2, v_inicial + WIDTH//2)

                # calcula a lista de pontos
                resp_outros = []
                for i in bbox[1]:
                    temp = self.pcloud.converter_2D_3D_unico(i[0], i[1])
                    resp_outros.append(temp)

                # calcula todos os pontos
                resp_todos = self.pcloud.converter_2D_3D(u_inicial, v_inicial, HEIGHT, WIDTH)

                # Guarda todas as respostas na variavel ENVIO
                temp = []
                temp.append(resp_centro)
                temp.append(resp_outros)
                temp.append(resp_todos)
                self.pcloud.ENVIO.append(temp)

            # imprime os tempos de processamento e da frame
            print('tempo calculo = ', time.perf_counter() - self.tempo_calculo)   # imprime o tempo de calculo em segundos
            print('tempo frame = ', time.perf_counter() - self.tempo_frame)   # imprime o tempo de calculo em segundos
            self.tempo_frame = time.perf_counter()

            # desenha tudo na janela da imagem 2D
            
            if flag_show_rgb_depth:
                self.pcloud.update_imagem()
            else:
                t_ = self.pcloud.depth_img_pc.copy()
                _, maximo, _, _= cv2.minMaxLoc(t_)
                t_ = t_ / maximo * 255 
                t_ = t_.astype(np.uint8)
                cv2.imshow(nome, t_)

            if GRAF3D == 1:
                self.pcloud.graficos() # mostra os graficos


            """
            self.tempinho = time.perf_counter()
            # self.pcloud.converter_2D_3D(y1, x1, HEIGHT, WIDTH)      # converte as coordenadas de (u,v) para 3D (x, y, z)
            # self.pcloud.converter_2D_3D(0, 0, height, width)      # converte as coordenadas de (u,v) para 3D (x, y, z)
            self.pcloud.converter_2D_3D(req.box_top_left_y, req.box_top_left_x, req.box_height, req.box_width)      # converte as coordenadas de (u,v) para 3D (x, y, z)
            print('tempo_conver = ', time.perf_counter() - self.tempinho)   # imprime o tempo de calculo em segundos
            self.tempinho = time.perf_counter()
            if GRAF3D == 1:
                self.pcloud.graficos()      # mostra os graficos



            # geometry_msgs/Point center_coords
            # geometry_msgs/Point[] requested_point_coords
            # geometry_msgs/Point[] bbox_point_coords

            answer = RetrievePointCloud()
            answer.center_coords.x = self.pcloud.FINAL1[0]
            answer.center_coords.y = self.pcloud.FINAL1[1]
            answer.center_coords.z = self.pcloud.FINAL1[2]
            print(answer.center_coords)
            print("----")

            for i in range(len(self.pcloud.FINAL2)):
                p = Point()
                p.x = self.pcloud.FINAL2[i][0]
                p.y = self.pcloud.FINAL2[i][1]
                p.z = self.pcloud.FINAL2[i][2]
                print(p)
                answer.requested_point_coords.append(p)
            print("====")

            if req.retrieve_bbox:
                for i in range(len(self.pcloud.FINAL3)):
                    p = Point()
                    p.x = self.pcloud.FINAL3[i][0]
                    p.y = self.pcloud.FINAL3[i][1]
                    p.z = self.pcloud.FINAL3[i][2]
                    answer.bbox_point_coords.append(p)

                    print(p)
                print("####")
            self.retrieve_point_cloud_publisher.publish(answer)
            """


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudNode()
    rclpy.spin(node)
    rclpy.shutdown()