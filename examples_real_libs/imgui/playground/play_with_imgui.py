import lg_imgui as imgui


ctx = imgui.create_context()
io = imgui.get_io()

# Build atlas
io.fonts.build()

# for n in range(20):
# print(f"NewFrame {n}")
io.display_size = imgui.ImVec2(1920, 1080)
iod = io.display_size
io.delta_time = 1.0 / 60.0

imgui.new_frame()

r = imgui.show_demo_window(None)

imgui.text("Hello, world")


def play_with_boxed_types():
    f = imgui.BoxedFloat(0.0)
    imgui.slider_float("float", f, 0.0, 1.0)

    my_str = imgui.BoxedString("Hello")
    imgui.input_text("Text", my_str, imgui.ImGuiInputTextFlags_.auto_select_all)


def play_with_multiple_return():
    f = 5.0
    changed, f2 = imgui.slider_float("Enter value", f, 0.0, 1.0)
    assert changed == False
    assert f2 == 5.0

    text = "A"
    changed, new_text = imgui.input_text("Enter Text", text)
    assert changed == False
    assert new_text == "A"

    values = [1.0, 2.0, 3.0]
    r = imgui.input_float3("Values", values)
    assert r == (False, [1.0, 2.0, 3.0])


# play_with_boxed_types()
play_with_multiple_return()

imgui.render()

imgui.destroy_context()
