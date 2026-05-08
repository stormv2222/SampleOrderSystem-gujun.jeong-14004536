from views.main_view import MainView
from views.sample_view import SampleView
from views.order_view import OrderView
from models.sample import SampleRepository
from models.order import OrderRepository
from models.inventory import InventoryRepository
from controllers.main_controller import MainController
from controllers.sample_controller import SampleController
from controllers.order_controller import OrderController
from models.production_queue import ProductionQueue

if __name__ == "__main__":
    main_view      = MainView()
    sample_repo    = SampleRepository("data/sample.json")
    sample_view    = SampleView()
    sample_ctrl    = SampleController(sample_repo, sample_view)
    order_repo     = OrderRepository("data/order.json")
    inventory_repo = InventoryRepository("data/inventory.json")
    production_queue = ProductionQueue()
    order_view     = OrderView()
    order_ctrl     = OrderController(order_repo, sample_repo, inventory_repo, production_queue, order_view)
    ctrl = MainController(main_view, sample_ctrl=sample_ctrl, order_ctrl=order_ctrl)
    ctrl.run()
