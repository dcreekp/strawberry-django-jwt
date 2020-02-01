import graphene

import graphql_jwt
from graphql_jwt.settings import jwt_settings
from graphql_jwt.utils import get_payload

from .context_managers import back_to_the_future
from .testcases import CookieTestCase


class TokenAuthTests(CookieTestCase):
    query = '''
    mutation TokenAuth($username: String!, $password: String!) {
      tokenAuth(username: $username, password: $password) {
        token
      }
    }'''

    class Mutation(graphene.ObjectType):
        token_auth = graphql_jwt.ObtainJSONWebToken.Field()

    def test_token_auth(self):
        response = self.execute({
            self.user.USERNAME_FIELD: self.user.get_username(),
            'password': 'dolphins',
        })

        token = response.cookies.get(jwt_settings.JWT_COOKIE_NAME).value
        payload = get_payload(token)

        self.assertIsNone(response.errors)
        self.assertEqual(token, response.data['tokenAuth']['token'])
        self.assertUsernameIn(payload)


class RefreshTokenTests(CookieTestCase):
    query = '''
    mutation {
      refreshToken {
        token
        payload
      }
    }'''

    class Mutation(graphene.ObjectType):
        refresh_token = graphql_jwt.Refresh.Field()

    def test_refresh(self):
        self.set_cookie()

        with back_to_the_future(seconds=1):
            response = self.execute()

        data = response.data['refreshToken']
        token = data['token']

        self.assertIsNone(response.errors)
        self.assertNotEqual(token, self.token)
        self.assertUsernameIn(data['payload'])