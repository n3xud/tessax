import pytest
from tessax.html_reader import req_html, format
from bs4 import BeautifulSoup


def test_ivalid_page():

    assert req_html("https://random_url/anothersub/sub") is None

    assert req_html("htps::/error") is None


def test_html_format():

    formatted = format(
        BeautifulSoup(
            """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Page Title</title>
                <div>useless stuff</div>
            </head>
            <body>

            <div>
                <h1>This is a Heading</h1>
                <p>This is a paragraph.</p>
                <div>
                    <div>
                        another div will be unwrapped
                    </div>
                </div>
            </div>

            <p>This is a paragraph.</p>
            <p>    </p>
            <!-- comment -->
            <div>
                <div>
                    <h1>This is a Heading 2</h1>
                    <p>This is a paragraph 2.</p>
                </div>
            </div>

            </body>
        </html>""".strip(),
            "html.parser",
        )
    )

    expected = BeautifulSoup(
        """
        <!DOCTYPE html>
        <title>Page Title</title>     
        <body>
            <div>
                <h1>This is a Heading</h1>
                <p>This is a paragraph.</p>
                <div>
                    another div will be unwrapped
                </div>
            </div>
            
            <p>This is a paragraph.</p>
            <div>
                <h1>This is a Heading 2</h1>
                <p>This is a paragraph 2.</p>
            </div>
        </body>
        """.strip(),
        "html.parser",
    )

    assert formatted.prettify() == expected.prettify()
