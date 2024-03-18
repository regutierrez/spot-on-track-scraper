import requests
from bs4 import BeautifulSoup as bs


def spotontrack_login(credentials: dict[str, str]) -> requests.Response:
    login_url: str = "https://www.spotontrack.com/login"
    username: str = "gutierrez.rafael23e@gmail.com"
    password: str = "decode-armoire-recopy9-donut-unmanaged"

    # might need to add this as arg for session.get in the future
    """
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
    )

    headers: dict[str, str] = {"User-Agent": user_agent}
    """

    with requests.Session() as session:
        response_content: str = session.get(login_url)._content
        html: bs = bs(response_content, "html.parser")
        auth_token: str = html.find("input", attrs={"name": "_token"}).attrs["value"]

        payload: dict[str, str] = {
            "email": username,
            "password": password,
            "_token": auth_token,
        }

        return session.post(login_url, data=payload)


def main():
    site: requests.Response = spotontrack_login()
    print(site.url, site.status_code)  # should print https://www.spotontrack.com/ 200


if __name__ == "__main__":
    main()
