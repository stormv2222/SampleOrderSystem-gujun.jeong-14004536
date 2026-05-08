from views.main_view import MainView
from controllers.main_controller import MainController

if __name__ == "__main__":
    view = MainView()
    ctrl = MainController(view)
    ctrl.run()
1