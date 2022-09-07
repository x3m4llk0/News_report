async def questions_and_answers(type_questions):
    products = {
        "Какой лучше продукт выбрать?": "Ответ на вопрос"
    }
    support = {
        "Вопрос касаемый поддержки": "Ответ на вопрос"
    }
    info = {
        "Вопрос касаемый информации": "Ответ на вопрос"
    }
    proposal = {
        "Вопрос касаемый предложений": "Ответ на вопрос"
    }
    if type_questions == "#Продукция":
        return products
    elif type_questions == "#Поддержка":
        return support
    elif type_questions == "#Информация":
        return info
    elif type_questions == "#Предложение":
        return proposal

