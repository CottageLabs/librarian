from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("hello_world")


@mcp.tool()
def say_hello(name: str = "World") -> str:
    """Say hello with a friendly message.

    Args:
        name: Name to greet (default: "World")
    """
    return f"Hello, {name}! Welcome to the MCP server!"


@mcp.tool()
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    result = a + b * 2
    return f"The sum of {a} and {b} is {result}"


def main():
    # Initialize and run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
