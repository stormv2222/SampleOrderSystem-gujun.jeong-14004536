from views.main_view import MainView
from views.sample_view import SampleView
from models.sample import SampleRepository
from controllers.main_controller import MainController
from controllers.sample_controller import SampleController

if __name__ == "__main__":
    main_view   = MainView()
    sample_repo = SampleRepository("data/sample.json")
    sample_view = SampleView()
    sample_ctrl = SampleController(sample_repo, sample_view)
    ctrl = MainController(main_view, sample_ctrl=sample_ctrl)
    ctrl.run()
