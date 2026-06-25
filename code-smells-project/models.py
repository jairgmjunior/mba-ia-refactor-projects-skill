from src.config.database import get_db
from src.models.product_model import create_product as criar_produto
from src.models.product_model import delete_product as deletar_produto
from src.models.product_model import get_product as get_produto_por_id
from src.models.product_model import list_products as get_todos_produtos
from src.models.product_model import search_products as buscar_produtos
from src.models.product_model import update_product as atualizar_produto
from src.models.user_model import authenticate as login_usuario
from src.models.user_model import create_user as criar_usuario
from src.models.user_model import get_user as get_usuario_por_id
from src.models.user_model import list_users as get_todos_usuarios
from src.models.order_model import create_order as criar_pedido
from src.models.order_model import list_orders as get_todos_pedidos
from src.models.order_model import list_user_orders as get_pedidos_usuario
from src.models.order_model import sales_report as relatorio_vendas
from src.models.order_model import update_order_status as atualizar_status_pedido
