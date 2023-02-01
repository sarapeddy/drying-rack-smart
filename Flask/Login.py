class Login:
    # Per usare la classe Login: passare al costruttore direttamente il cursore di una connessione a mysql già stabilita
    # e user e pwd
    def __init__(self, cur):
        self.cur = cur

    def check_db(self, username, password):
        if username is None or password is None:
            return 'Please insert a correct user and a correct password'
        # seleziona user e pin
        query = f"select user_name, pin " \
                f"from rack_user " \
                f"where user_name like " \
                f"'{username}' ;"
        self.cur.execute(query)
        result = self.cur.fetchall()

        if not result:
            return 'Please insert a correct user and a correct password'

        current_user = result[0][0]
        current_pin = result[0][1]

        if username == current_user and password == current_pin:
            return current_user

        return 'Please insert a correct user and a correct password'
