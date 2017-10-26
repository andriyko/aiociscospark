import json

from .context import aiociscospark


def test_spark_response_error(event_loop, test_url, response_not_found_error, fake_resp_error):
    resp = event_loop.run_until_complete(fake_resp_error)
    spark_error = event_loop.run_until_complete(
        aiociscospark.exceptions.SparkResponseError.get(resp)
    )
    assert spark_error.text == json.dumps(response_not_found_error)
    assert spark_error.json == response_not_found_error
    assert spark_error.error_code is None
    assert spark_error.tracking_id == 'NA_54fe2133-6126-4312-a213-c09ee7536d85'
    assert spark_error.message == 'Person not found'
    assert spark_error.errors == [{'description': 'Person not found'}]
    assert str(spark_error) == f"Request: GET {test_url}. " \
                               "Reply [404]: 'Person not found'. errorCode=None, " \
                               "errors=[{'description': 'Person not found'}]"
    assert spark_error._response.closed is True


def test_spark_response_error_rate_limit(event_loop, fake_resp_error_rate_limit):
    resp = event_loop.run_until_complete(fake_resp_error_rate_limit)
    spark_error = event_loop.run_until_complete(
        aiociscospark.exceptions.SparkRateLimitExceeded.get(resp)
    )
    assert spark_error.retry_after == 60
    assert spark_error.json == {}


def test_spark_response_error_repr(event_loop, fake_resp_error_rate_limit,
                                   response_headers_retry_after):
    resp = event_loop.run_until_complete(fake_resp_error_rate_limit)
    spark_error = event_loop.run_until_complete(
        aiociscospark.exceptions.SparkRateLimitExceeded.get(resp)
    )
    assert str(spark_error) == f"Request: GET https://api.ciscospark.com/v1/people. " \
                               f"Reply [429]: ''. Headers: {response_headers_retry_after}"
