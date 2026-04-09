class App:
    def __init__(self):
        self.features = None

    def get_features(self):
        if not self.features:
            self.features = self.call("GET", "/api/v1/app/features")

        return self.features

    def find_feature(self, feature_name: str):
        feature = [r for r in self.get_features() if r.get("name") == feature_name]
        if not feature:
            return None

        return feature[0]
