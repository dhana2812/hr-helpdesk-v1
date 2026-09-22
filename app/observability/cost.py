from decimal import Decimal


# OpenRouter published pricing for openai/gpt-5.4.
#
# Price is expressed as USD per 1 million tokens.
INPUT_PRICE_PER_MILLION = Decimal("2.50")
OUTPUT_PRICE_PER_MILLION = Decimal("15.00")


def calculate_request_cost(
    input_tokens: int,
    output_tokens: int,
) -> Decimal:
    """
    Calculate the estimated request cost in USD.

    Pricing:
        Input  = $2.50 per 1,000,000 tokens
        Output = $15.00 per 1,000,000 tokens
    """

    input_cost = (
        Decimal(input_tokens)
        / Decimal("1000000")
        * INPUT_PRICE_PER_MILLION
    )

    output_cost = (
        Decimal(output_tokens)
        / Decimal("1000000")
        * OUTPUT_PRICE_PER_MILLION
    )

    return input_cost + output_cost


def calculate_request_cost_float(
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Return the request cost as a float for JSON logging.
    """

    return float(
        calculate_request_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    )
