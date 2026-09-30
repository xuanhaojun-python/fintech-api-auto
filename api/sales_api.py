from api.base_client import BaseClient


class SalesAPI(BaseClient):
    """销售数据查询接口"""

    def query_sales(self, table_name: str, account_id: str,
                    start_id: int = 0, limit: int = 10):
        """查询销售数据 POST /v1/sales/query"""
        return self.post(
            "/v1/sales/query",
            headers={"X-ON-BEHALF-OF": account_id},
            json={"tableName": table_name, "startId": start_id, "limit": limit},
        )
