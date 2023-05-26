import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL import GL as gl
from src.app import App
import multiprocessing

def main():
    # Initialize GLFW
    if not glfw.init():
        exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    window = glfw.create_window(1280, 720, "AutoCaz - Facial Recognition OBS Server", None, None)
    if not window:
        glfw.terminate()
        exit(1)

    glfw.make_context_current(window)
    imgui.create_context()
    renderer = GlfwRenderer(window)

    app = App()

    if not app.Setup():
        print("Error: Can't setup app")
        glfw.terminate()
        exit(1)

    # main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()
        renderer.process_inputs()
        # Set the clear color and clear the screen
        gl.glClearColor(0.3, 0.3, 0.3, 1)  # Set the background color (R, G, B, A)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.new_frame()

        App.AppMainLoop(app)
        
        imgui.render()
        imgui.end_frame()
        try:
            renderer.render(imgui.get_draw_data())
        except:
            print("Render: Glitch!")
            
        glfw.swap_buffers(window)
    # End of main loop

    app.Teardown()

    # Clean up
    renderer.shutdown()  
    glfw.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
