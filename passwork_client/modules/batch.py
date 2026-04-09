class Batch:
    """
        Batch request method
    """
    def send_batch(self, requests: list):

        batch = 25
        response = []

        batch_requests = [requests[i:i + batch] for i in range(0, len(requests), batch)]
        for batch_request in batch_requests:
            response.extend(self.batch_request(batch_request))

        return response

    def batch_request(self, requests: list):
        responses = self.call("POST", "/api/v1/batch", {"requests": requests})

        response_data = []
        for response in responses["responses"]:
            if response["statusCode"] == 200:
                response_data.append(response["body"])

        return response_data
