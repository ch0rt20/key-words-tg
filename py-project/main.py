from ctypes.util import find_library
from ctypes import *
import json
import sys

# Загрузка dll библиотеки
tdjson_path = 'C:/td/tdlib/bin/tdjson.dll'
if tdjson_path is None:
    sys.exit("Can't find 'tdjson' library")
tdjson = CDLL(tdjson_path)

# загрузка функций TDLib из общей библиотеки
_td_create_client_id = tdjson.td_create_client_id
_td_create_client_id.restype = c_int
_td_create_client_id.argtypes = []

_td_receive = tdjson.td_receive
_td_receive.restype = c_char_p
_td_receive.argtypes = [c_double]

_td_send = tdjson.td_send
_td_send.restype = None
_td_send.argtypes = [c_int, c_char_p]

_td_execute = tdjson.td_execute
_td_execute.restype = c_char_p
_td_execute.argtypes = [c_char_p]

log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)

_td_set_log_message_callback = tdjson.td_set_log_message_callback
_td_set_log_message_callback.restype = None
_td_set_log_message_callback.argtypes = [c_int, log_message_callback_type]

# инициализируем TDLib лог с нужными параметрами
@log_message_callback_type
def on_log_message_callback(verbosity_level, message):
    if verbosity_level == 0:
        sys.exit('TDLib fatal error: %r' % message)

#
def td_execute(query):
    query = json.dumps(query).encode('utf-8')
    result = _td_execute(query)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

_td_set_log_message_callback(2, on_log_message_callback)

# устанавливаем 1-й уровень детализации журнала TDLib
print(str(td_execute({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1, '@extra': 1.01234})).encode('utf-8'))


# создаем клиент
client_id = _td_create_client_id()

def td_send(query):
    query = json.dumps(query).encode('utf-8')
    _td_send(client_id, query)

def td_receive():
    result = _td_receive(1.0)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

print(str(td_execute({'@type': 'getTextEntities', 'text': '@telegram /test_command https://telegram.org telegram.me', '@extra': ['5', 7.0, 'a']})).encode('utf-8'))

# запуск клиента, отправляя на него запрос
td_send({'@type': 'getOption', 'name': 'version', '@extra': 1.01234})

# цикл с основными событиями
while True:
    event = td_receive()
    if event:
        # стадии процесса авторизации
        if event['@type'] == 'updateAuthorizationState':
            auth_state = event['authorization_state']

            # если клиент закрыт, нужно его отключить и создать новый
            if auth_state['@type'] == 'authorizationStateClosed':
                break

            # устанавливаем параметры TDLib
            # api_id и api_hash мы берем здесь: https://my.telegram.org
            # вставляем сюда
            if auth_state['@type'] == 'authorizationStateWaitTdlibParameters':
                td_send({'@type': 'setTdlibParameters',
                         'database_directory': 'tdlib',
                         'use_message_database': True,
                         'use_secret_chats': True,
                         'api_id': 18947603,
                         'api_hash': '051967453854c51ce8ee51f075e75c87',
                         'system_language_code': 'en',
                         'device_model': 'Desktop',
                         'application_version': '1.0',
                         'enable_storage_optimizer': True})

            # вход по номеру телефона
            if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
                phone_number = input('Please enter your phone number: ')
                td_send({'@type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})

            # вход по email
            if auth_state['@type'] == 'authorizationStateWaitEmailAddress':
                email_address = input('Please enter your email address: ')
                td_send({'@type': 'setAuthenticationEmailAddress', 'email_address': email_address})

            # ожидание кода авторизации с мыла
            if auth_state['@type'] == 'authorizationStateWaitEmailCode':
                code = input('Please enter the email authentication code you received: ')
                td_send({'@type': 'checkAuthenticationEmailCode',
                         'code': {'@type': 'emailAddressAuthenticationCode', 'code' : code}})

            # ожидание кода авторизации
            if auth_state['@type'] == 'authorizationStateWaitCode':
                code = input('Please enter the authentication code you received: ')
                td_send({'@type': 'checkAuthenticationCode', 'code': code})

            # вход по имени и фамилии
            if auth_state['@type'] == 'authorizationStateWaitRegistration':
                first_name = input('Please enter your first name: ')
                last_name = input('Please enter your last name: ')
                td_send({'@type': 'registerUser', 'first_name': first_name, 'last_name': last_name})

            # ожидание паспорта, если имеется
            if auth_state['@type'] == 'authorizationStateWaitPassword':
                password = input('Please enter your password: ')
                td_send({'@type': 'checkAuthenticationPassword', 'password': password})

        # запуск нового потока с передачей параметра event для дальнейшей сортировки

        print(str(event).encode('utf-8'))
        sys.stdout.flush()

