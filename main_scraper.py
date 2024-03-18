import requests
import bs4


def login_to_site():
    login_url: str = "https://www.spotontrack.com/login"
    username = "gutierrez.rafael23e@gmail.com"
    password = "decode-armoire-recopy9-donut-unmanaged"

    with requests.session() as login:
        request = login.get(login_url).text
        html = bs4(request, "html.parser")
        auth_token = html.find(name="input", attrs={"name": "_token"}).get_text()

    payload: dict[str, str] = {
        "user": username,
        "password": password,
        "token": auth_token,
    }

    return login.post(login_url, data=payload)


def main():
    site = login_to_site()


if __name__ == "__main__":
    main()
