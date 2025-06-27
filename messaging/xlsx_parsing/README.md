## Queue worker and server for xlsx_parsing

- Ensure you run the `app.py` from the `xlsx_parsing` microservice
- Run also the rpc server and the worker as following
- For the server, from the `messaging/xlsx_parsing` dir:
```python
fastapi run xlsx_parsing_rpc_server.py --port 8005
```
- For the worker, from `messaging` dir:
```python
python -m xlsx_parsing.xlsx_parsing_worker
```