from langchain.tools import tool

@tool(return_direct=True)
def retrieve_products(query: str) -> str:
    """Find and suggest products from catalog based on users needs or preferences in the query. 
    Requires full 'input' question as query.
    Useful for when a user is searching for products, asking for details,
    or want to buy some product.
    Useful for finding products with name, description, color, size, weight and other product attributes.
    Return the output without processing further.
    """
    output = ''

    return output