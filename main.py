import requests
from bs4 import NavigableString, Tag
from bs4 import BeautifulSoup as bs


def spotontrack_login(username: str, password: str) -> requests.Session:
    # MIGHT BE BETTER TO MAKE A SEPARATE FUNCTION FOR CREATING A NEW SESSION

    login_url: str = "https://www.spotontrack.com/login"
    # might need to add this as arg for session.get in the future
    """
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
    )

    headers: dict[str, str] = {"User-Agent": user_agent}
    """

    session: requests.Session = requests.Session()
    response_content: bytes | None = session.get(login_url)._content
    if response_content is None:
        raise Exception("Website HTML contents not found. Quitting script")

    html: bs = bs(response_content, "html.parser")
    auth_token_tag: Tag | NavigableString | None = html.find(
        "input", attrs={"name": "_token"}
    )

    if isinstance(auth_token_tag, Tag):
        auth_token: str = auth_token_tag.attrs["value"]
    else:
        raise Exception(
            "HTML tag where token is located was not found. Quitting script..."
        )

    if auth_token is None or auth_token == "":
        raise Exception("CSRF token not found. Quitting script...")

    payload: dict[str, str] = {
        "email": username,
        "password": password,
        "_token": auth_token,
    }

    login = session.post(login_url, data=payload)

    if login.status_code != 200:
        raise Exception("Login failed. Quitting script...")

    return session


def main():
    username: str = "gutierrez.rafael23e@gmail.com"
    password: str = "decode-armoire-recopy9-donut-unmanaged"
    try:
        session: requests.Session = spotontrack_login(username, password)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
