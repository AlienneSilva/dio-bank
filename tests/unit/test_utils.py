#Por padrão tem que colocar no arquivo de teste e no metodo "test_"
import pytest
from src.utils import eleva_quadrado, required_role
from http import HTTPStatus

@pytest.mark.parametrize("test_input,expected", [(2, 4), (10, 100), (3, 9)])
def test_eleva_quadrado_sucesso(test_input, expected):
    resultado = eleva_quadrado(test_input)
    assert resultado == expected

@pytest.mark.parametrize(
        "test_input, exc_class, msg",
        [
            ("a", TypeError, "unsupported operand type(s) for ** or pow(): 'str' and 'int'"),
            (None, TypeError, "unsupported operand type(s) for ** or pow(): 'NoneType' and 'int'"),
        ],)
def test_eleva_quadrado_falha(test_input, exc_class, msg):
    with pytest.raises(exc_class) as exc:
        eleva_quadrado(test_input)
    assert str(exc.value) == msg

def test_required_role_success(mocker):
    #Give (forneço para meu teste)
    mock_user = mocker.Mock()
    mock_user.role.name = "Admin"
    mocker.patch("src.utils.get_jwt_identity")
    mocker.patch("src.utils.db.get_or_404", return_value =mock_user)        
    decorated_function = required_role("Admin")(lambda: "Success")
    #When (Executo)
    result = decorated_function()
    #Then (Verifico)
    assert result == "Success"

def test_required_role_fail(mocker):
    #Give (forneço para meu teste)
    mock_user = mocker.Mock()
    mock_user.role.name = "Normal"
    mocker.patch("src.utils.get_jwt_identity")
    mocker.patch("src.utils.db.get_or_404", return_value =mock_user)        
    decorated_function = required_role("Admin")(lambda: "Success")
    #When (Executo)
    result  = decorated_function()
    #Then (Verifico)
    assert result == ({"message": "User don't have access."}, HTTPStatus.FORBIDDEN)
