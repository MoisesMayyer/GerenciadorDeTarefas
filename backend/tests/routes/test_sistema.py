
def test_raiz(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["message"] == "teste"