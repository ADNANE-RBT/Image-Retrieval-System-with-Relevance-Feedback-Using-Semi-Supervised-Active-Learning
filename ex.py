import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# Points de contrôle initiaux (3x3 grid pour une surface de Bézier quadratique)
control_points = np.array([
    [[-1.5, -1.5, 0.0], [-0.5, -1.5, 0.0], [0.5, -1.5, 0.0]],
    [[-1.5, 0.0, 1.0], [-0.5, 0.0, 1.0], [0.5, 0.0, 1.0]],
    [[-1.5, 1.5, 0.0], [-0.5, 1.5, 0.0], [0.5, 1.5, 0.0]]
], dtype=float)

current_point = [0, 0]  # Point de contrôle courant (ligne, colonne)
signe = 1               # Direction de modification (+1 ou -1)
pasX, pasY, pasZ = 0.1, 0.1, 0.1  # Pas pour chaque axe

def bezier_surface():
    """Dessine la surface de Bézier à partir des points de contrôle."""
    glMap2f(GL_MAP2_VERTEX_3,
            0, 1, 3, 3,  # Dimension en u
            0, 1, 9, 3,  # Dimension en v
            control_points)
    glEnable(GL_MAP2_VERTEX_3)
    glMapGrid2f(20, 0.0, 1.0, 20, 0.0, 1.0)
    glEvalMesh2(GL_FILL, 0, 20, 0, 20)

def display():
    """Fonction de rendu."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()

    # Dessine la surface de Bézier
    glColor3f(0.6, 0.6, 1.0)
    bezier_surface()

    # Dessine les points de contrôle
    glPointSize(5.0)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    for i in range(3):
        for j in range(3):
            glVertex3fv(control_points[i][j])
    glEnd()

    glPopMatrix()
    glutSwapBuffers()

def keyboard(key, x, y):
    """Gestion des touches clavier."""
    global current_point, signe

    if key == b'x':
        control_points[current_point[0]][current_point[1]][0] += signe * pasX
    elif key == b'y':
        control_points[current_point[0]][current_point[1]][1] += signe * pasY
    elif key == b'z':
        control_points[current_point[0]][current_point[1]][2] += signe * pasZ
    elif key == b's':
        signe *= -1
    elif key == b'\t':
        current_point[1] = (current_point[1] + 1) % 3
        if current_point[1] == 0:
            current_point[0] = (current_point[0] + 1) % 3

    glutPostRedisplay()

def reshape(w, h):
    """Adapte la scène lorsque la fenêtre est redimensionnée."""
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w) / float(h), 1.0, 20.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

def init():
    """Initialise les paramètres OpenGL."""
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)

if __name__ == "__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow()
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()
