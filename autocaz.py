import glfw
import imgui
import src.theme as theme
from imgui.integrations.glfw import GlfwRenderer
from OpenGL import GL as gl
from src.app import App
import multiprocessing
import time
from time import perf_counter

#stats
app_frame_count = 0
app_start_time = perf_counter()
app_fps = 0

#control
desired_fps = 60.0
frame_duration = 1.0 / desired_fps  # The duration each frame should last
prev_frame_time = time.time()


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

    theme.load_default_style()

    # loading screen
    gl.glClearColor(0.3, 0.3, 0.3, 1)  # Set the background color (R, G, B, A)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    imgui.new_frame()
    imgui.text("Loading ...") 
    imgui.render()
    imgui.end_frame()
    try:
        renderer.render(imgui.get_draw_data())
    except:
        pass                       
    glfw.swap_buffers(window)
    # end of loading screen

    # create the app
    app = App()
    if not app.Setup():
        print("Error: Can't setup app")
        glfw.terminate()
        exit(1)

    prev_frame_time = time.time()

    # main loop
    while not glfw.window_should_close(window):
      
        def do_draw():
            glfw.poll_events()
            renderer.process_inputs()
            # Set the clear color and clear the screen
            gl.glClearColor(0.3, 0.3, 0.3, 1)  # Set the background color (R, G, B, A)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.new_frame()
            App.AppUI(app)  
            imgui.render()
            imgui.end_frame()
            try:
                renderer.render(imgui.get_draw_data())
            except:
                print("Render: Glitch!")                
            glfw.swap_buffers(window)


        current_time = time.time()
        if current_time - prev_frame_time >= frame_duration:
            do_draw()
            prev_frame_time = current_time
        
        App.AppMainLoop(app)
      
      
    # End of main loop

    app.Teardown()

    # Clean up
    renderer.shutdown()  
    glfw.terminate()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
