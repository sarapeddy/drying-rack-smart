class Login:
    # Per usare la classe Login: passare al costruttore direttamente il cursore di una connessione a mysql già stabilita
    # e user e pwd
    def __init__(self, cur):
        self.cur = cur

    def lat_lon_control(self, lat, lon):
        lat = int(lat)
        lon = int(lon)
        if (lat < -90) or (lat > 90):
            return 'Insert a correct latitude'
        elif (lon < -180) or (lon > 180):
            return 'Insert a correct longitude'

        return 'ok'

    def check_pwd(self, pwd):
        if len(pwd) < 8:
            return False
        return True

    def check_db(self, username, password):
        if username is None or password is None:
            return 'Please insert a correct user and a correct password'

        if not self.check_pwd(password):
            return 'Please insert a correct password'

        # seleziona user e pin
        query = f"select user_name " \
                f"from rack_user "
        self.cur.execute(query)
        result = self.cur.fetchall()

        print(result)

        if not result:
            return 'Please insert a correct user and a correct password'

        if username in result:
            return 'Username already in use'

        return 'ok'
