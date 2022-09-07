from aiogram.filters.callback_data import CallbackData


class ProductsCallback(CallbackData, prefix="products"):
    id: int

