async def questions_and_answers(type_questions):
    products = {
        "Где я могу купить продукцию SPLAT GLOBAL?":
            "Ознакомиться с полным ассортиментом продукции SPLAT® "                                    
            "вы можете на онлайн площадках, например OZON, Wildberries,  "
            "Yandex Market, AliExpress! Также вы можете найти наши продукты в "
            "национальных сетевых магазинах Пятерочка, Дикси, Магнит, розничных "
            "магазинах и аптеках вашего города. Также наша продукция широко представлена "
            "в крупных гипермаркетах, таких как Лента, Ашан, Перекресток."
    }
    support = {
        "Не нашли ответа на свой вопрос?": "Задайте его в окошке меню «Задать свой вопрос».",
        "Что делать, если чат-бот не отвечает на команды?": "Подробно опишите свою проблему в окошке меню «Задать свой вопрос».",
        "Мне не пришел ответ на мой вопрос, заданный в чат-боте. Что делать? ":
            "Пожалуйста, напишите нам на почту actions@splat.ru либо задайте свой вопрос "
            "в форме обратной связи на нашем официальном сайте: https://splatglobal.com/ru/help"
    }
    info = {
        "Где я могу получить информацию о продукции компании SPLAT Global?":
            "Всю информацию вы можете получить на наших официальных сайтах. "
            "Там же вы задать вопрос, если вдруг здесь не нашли на него ответ. \n\n"
            "Официальные сайты компании:\n"
            "https://splatglobal.com/ru\n"
            "https://biomio.ru/\n"
            "https://biomedglobal.net/\n"
            "https://splat-innova.com/\n"
            "Ссылка на форму обратной связи:\n"
            "https://splatglobal.com/ru/help"
    }
    proposal = {
        "Могу ли я пригласить друга участвовать в программе?":
            "Стать участником программы возможно только после самостоятельной подачи "
            "заявки на сайте https://promo.splatglobal.com/friends/. Вы можете отправить ссылку "
            "на сайт вашему другу, чтобы он сам заполнил регистрационную форму.",
        "Кто может стать участником?": "Люди, достигшее 18 лет и постоянно проживающие на территории РФ и СНГ.",
        "Есть ли вознаграждение?":
            "Становясь участником программы и активно участвуя в тестах продукции, опросах, "
            "обсуждениях и мероприятиях, вы сможете получать от нас бесплатные наборы наших продуктов, "
            "скидки и дополнительные бонусы от SPLAT GLOBAL.",
        "Что будут делать участники?":
            "Тестировать новинки, голосовать за лучшие идеи и дизайны, обсуждать актуальные вопросы на тему ухода "
            "за собой, а также получать эксклюзивную информацию от экспертов компании SPLAT GLOBAL.",
        "Где посмотреть правила участия?":
            "Полные правила участия в программе вы всегда можете найти в этом чат-боте, нажав на кнопку "
            "«Правила Участия в программе».",
        "Можно ли делиться информацией из программы с другими людьми?":
            "Участники получат доступ к конфиденциальной информации, поэтому по нашим правилам делиться "
            "материалами программы с другими людьми запрещено.",
        "Как я могу выйти из программы?":
            "Если вы больше не хотите быть участником программы, то нажмите на кнопку «Покинуть Сообщество» "
            "в этом чат-боте и ваш доступ к программе будет деактивирован."
    }
    if type_questions == "#Продукция":
        return products
    elif type_questions == "#Поддержка":
        return support
    elif type_questions == "#Информация":
        return info
    elif type_questions == "#Программа":
        return proposal
