import tracemalloc
tracemalloc.start()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes
import key

app = ApplicationBuilder().token(key.TOKEN).build()

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "¡Bienvenido a Base Calculator Bot!\n\n"
        "Este bot te permite realizar cálculos en diferentes bases numéricas.\n\n"
        "Pasos para usar el bot:\n"
        "1. Usa el comando /start para iniciar el bot y seleccionar la base numérica.\n"
        "2. Selecciona la base numérica (Decimal, Binario, o Hexadecimal) usando los botones.\n"
        "3. Utiliza el comando /calc seguido de una expresión matemática en la base seleccionada.\n\n"
        "Ejemplo de uso:\n"
        "/calc 10 + 5  # Realiza la suma en base decimal\n"
        "/calc 1010 + 1101  # Realiza la suma en base binaria\n"
        "/calc A + B  # Realiza la suma en base hexadecimal\n\n"
        "¡Diviértete calculando en diferentes bases!"
    )
    await update.message.reply_text(help_text)

# Función para verificar si una cadena representa un número válido en una base dada
def is_valid_number(number_str, base):
    try:
        if '.' in number_str:
            float(number_str)  # Intenta convertir a float si es decimal
        else:
            int(number_str, base)
        return True
    except ValueError:
        return False

# Diccionario para mapear las bases a sus valores respectivos
BASE_MAPPING = {
    "decimal": 10,
    "binario": 2,
    "hexadecimal": 16,
}

# Función para verificar si una lista de cadenas representa números válidos en una base dada
def are_valid_numbers(parts, base):
    return all(is_valid_number(part, base) for part in parts)

# Función para manejar la operación matemática con números decimales
async def perform_calculation(update, selected_base, numero1, operador, numero2):
    try:
        # Realiza la operación matemática especificada por el usuario
        if operador == '+':
            resultado_decimal = numero1 + numero2
        elif operador == '-':
            resultado_decimal = numero1 - numero2
        elif operador == '*':
            resultado_decimal = numero1 * numero2
        elif operador == '/':
            # Maneja la división por cero
            if numero2 == 0:
                await update.message.reply_text('Error: División por cero no permitida.')
                return
            resultado_decimal = numero1 / numero2
        else:
            await update.message.reply_text('Operador no válido. Utiliza +, -, *, o /')
            return

        # Convierte el resultado a las bases especificadas
        resultado_binario = bin(int(resultado_decimal))[2:].replace('b', '')
        resultado_hexadecimal = hex(int(resultado_decimal))[2:].upper().replace('X','-')

        # Envía los resultados en todas las bases al usuario
        await update.message.reply_text(f'\U0001f522 Resultado en decimal: {resultado_decimal}')
        await update.message.reply_text(f'0\uFE0F\u20E3 Resultado en binario: {resultado_binario}')
        await update.message.reply_text(f'\U0001f520 Resultado en hexadecimal: {resultado_hexadecimal}')

    except ValueError:
        await update.message.reply_text(f'Error: Introduce números válidos en la base {selected_base}.')

# Función que maneja el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Envia un mensaje de bienvenida al usuario y muestra los botones inline para seleccionar la base.
    keyboard = [
        [
            InlineKeyboardButton("Decimal", callback_data="decimal"),
            InlineKeyboardButton("Binario", callback_data="binario"),
            InlineKeyboardButton("Hexadecimal", callback_data="hexadecimal"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('¡Bienvenido a Base Calculator Bot! Por favor, selecciona la base:', reply_markup=reply_markup)

# Función que maneja las selecciones de base con botones inline
async def base_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data['selected_base'] = query.data
    await query.message.edit_text(f'Seleccionaste la base: {query.data}')

# Función que realiza cálculos
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Obtiene el texto del mensaje después del comando /calc
    message_text = update.message.text[6:].strip()

    # Divide el mensaje en las partes (número1, operador, número2)
    parts = message_text.split()

    # Obtiene la base seleccionada previamente por el usuario
    selected_base = context.user_data.get('selected_base')

    if selected_base and selected_base in BASE_MAPPING:
        # Verifica si hay suficientes elementos en la lista y si son números válidos
        if len(parts) == 3:
            numero1_str, operador, numero2_str = parts

            # Verifica si los números proporcionados coinciden con la base seleccionada
            if not (is_valid_number(numero1_str, BASE_MAPPING[selected_base]) and is_valid_number(numero2_str, BASE_MAPPING[selected_base])):
                await update.message.reply_text(f'Error: Los números deben ser de la base {selected_base}.')
                return

            # Convierte los números a flotantes si es hexadecimal, de lo contrario a enteros
            if selected_base == 'hexadecimal':
                numero1 = int(numero1_str, 16)
                numero2 = int(numero2_str, 16)
            else:
                numero1 = float(numero1_str)
                numero2 = float(numero2_str)

            # Realiza la operación matemática
            await perform_calculation(update, selected_base, numero1, operador, numero2)
        else:
            await update.message.reply_text('Formato incorrecto. Utiliza /calc número operador número')
    else:
        await update.message.reply_text('Selecciona una base válida antes de realizar cálculos.')

# Agrega un manejador para el comando /help
app.add_handler(CommandHandler("help", help))

# Agrega un manejador para el comando /start
app.add_handler(CommandHandler("start", start))

# Agrega un manejador para las selecciones de base con botones inline
app.add_handler(CallbackQueryHandler(base_selection))

# Agrega un manejador para el comando /calc
app.add_handler(CommandHandler("calc", calculate))

# Inicia la aplicación y espera a que lleguen actualizaciones desde Telegram
if __name__ == "__main__":
    app.run_polling()
