from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView, Request, Response
from ApiRequesters.Auth.permissions import IsAuthenticated
from ApiRequesters.Auth.AuthRequester import AuthRequester
from ApiRequesters.Stats.decorators import collect_request_stats_decorator, CollectStatsMixin
from ApiRequesters.utils import get_token_from_request
from ApiRequesters.exceptions import BaseApiRequestError, UnexpectedResponse
from ApiRequesters.Places.PlacesRequester import PlacesRequester
from ApiRequesters.Users.UsersRequester import UsersRequester
from ApiRequesters.Awards.AwardsRequester import AwardsRequester


class BaseGatewayView(APIView, CollectStatsMixin):
    """
    Базовая вьюха для здешних
    """
    permission_classes = (IsAuthenticated, )

    def get_user_info(self, request):
        token = get_token_from_request(request)
        try:
            _, auth_json = AuthRequester().get_user_info(token)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом авторизации, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return auth_json

    def add_achievement(self, request: Request, achievement_id: int, auth_json: dict):
        """
        1 -- создание профиля
        2 -- Добавление места
        3 -- Оставил рейтинг
        4 -- Подтвердил существование
        5 -- Удалил существование
        6 -- Купил пин
        """
        try:
            _, token_json = AuthRequester().app_get_token(settings.APP_ID, settings.APP_SECRET)
            token = token_json['access']
            _, user_json = UsersRequester().add_achievement(user_id=auth_json['id'], achievement_id=achievement_id,
                                                            app_token=token)
            return user_json
        except (BaseApiRequestError, UnexpectedResponse):
            return

    def update_rating(self, request: Request, d_rating: int, auth_json: dict):
        try:
            _, token_json = AuthRequester().app_get_token(settings.APP_ID, settings.APP_SECRET)
            token = token_json['access']
            _, user_json = UsersRequester().change_rating(user_id=auth_json['id'], drating=d_rating, app_token=token)
            return user_json
        except BaseApiRequestError:
            return


class AddPlaceView(BaseGatewayView):
    """
    Добавление нового места
    """
    def post_place(self, request, auth_json):
        token = get_token_from_request(request)
        try:
            _, new_place = PlacesRequester().create_place(**request.data, created_by=auth_json['id'], token=token)
        except TypeError as e:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except UnexpectedResponse as e:
            return Response(e.body, status=e.code)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом мест, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return new_place

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_achievement_stats])
    def post(self, request: Request):
        auth_json = self.get_user_info(request)
        if isinstance(auth_json, Response):
            return auth_json
        new_place = self.post_place(request, auth_json)
        if isinstance(new_place, Response):
            return new_place
        stats_kwargs = []
        new_user = self.add_achievement(request, 2, auth_json)
        if new_user is not None:
            stats_kwargs = [{
                'request': request,
                'achievement_id': 2,
            }]
        new_user = self.update_rating(request, 1000, auth_json) or new_user
        ret_data = {
            'place': new_place,
            'profile': new_user,
        }
        return Response(ret_data, status=status.HTTP_201_CREATED), stats_kwargs


class AddRatingView(BaseGatewayView):
    """
    Добавление рейтинга
    """
    def post_rating(self, request, auth_json):
        token = get_token_from_request(request)
        try:
            _, new_rating = PlacesRequester().create_rating(**request.data, created_by=auth_json['id'], token=token)
        except TypeError:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except UnexpectedResponse as e:
            return Response(e.body, status=e.code)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом мест, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return new_rating

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_achievement_stats])
    def post(self, request: Request):
        auth_json = self.get_user_info(request)
        if isinstance(auth_json, Response):
            return auth_json
        new_rating = self.post_rating(request, auth_json)
        if isinstance(new_rating, Response):
            return new_rating
        stats_kwargs = []
        new_user = self.add_achievement(request, 3, auth_json)
        if new_user is not None:
            stats_kwargs = [{
                'request': request,
                'achievement_id': 3,
            }]
        new_user = self.update_rating(request, 30, auth_json) or new_user
        ret_data = {
            'rating': new_rating,
            'profile': new_user
        }
        return Response(ret_data, status=status.HTTP_201_CREATED), stats_kwargs


class AddAcceptView(BaseGatewayView):
    """
    Добавление подтверждения
    """
    def post_accept(self, request, auth_json):
        token = get_token_from_request(request)
        try:
            _, new_accept = PlacesRequester().create_acceptance(**request.data, created_by=auth_json['id'], token=token)
        except TypeError:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except UnexpectedResponse as e:
            return Response(e.body, status=e.code)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом мест, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return new_accept

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_achievement_stats])
    def post(self, request: Request):
        auth_json = self.get_user_info(request)
        if isinstance(auth_json, Response):
            return auth_json
        new_accept = self.post_accept(request, auth_json)
        if isinstance(new_accept, Response):
            return new_accept
        stats_kwargs = []
        new_user = self.add_achievement(request, 4, auth_json)
        if new_user is not None:
            stats_kwargs = [{
                'request': request,
                'achievement_id': 3,
            }]
        new_user = self.update_rating(request, 50, auth_json) or new_user
        ret_data = {
            'accept': new_accept,
            'profile': new_user
        }
        return Response(ret_data, status=status.HTTP_201_CREATED), stats_kwargs


class DeleteAcceptanceView(BaseGatewayView):
    """
    Удаление подтверждения
    """
    def delete_accept(self, request, acceptance_id):
        token = get_token_from_request(request)
        try:
            PlacesRequester().delete_acceptance(acceptance_id=acceptance_id, token=token)
        except TypeError:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except UnexpectedResponse as e:
            return Response(e.body, status=e.code)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом мест, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_achievement_stats])
    def delete(self, request: Request, acceptance_id):
        auth_json = self.get_user_info(request)
        if isinstance(auth_json, Response):
            return auth_json
        try:
            acceptance_id = int(acceptance_id)
        except ValueError:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        is_resp = self.delete_accept(request, acceptance_id)
        if isinstance(is_resp, Response):
            return is_resp
        # stats_kwargs = []
        # new_user = self.add_achievement(request, 5, auth_json)
        # if new_user is not None:
        #     stats_kwargs = [{
        #         'request': request,
        #         'achievement_id': 5,
        #     }]
        # new_user = self.update_rating(request, 50, auth_json) or new_user
        # ret_data = {
        #     'profile': new_user
        # }
        ret_data = {'hello', 'world'}
        return Response(data=ret_data, status=status.HTTP_204_NO_CONTENT) #, stats_kwargs


class BuyPinView(BaseGatewayView):
    """
    Покупка пина
    """
    def buy_pin(self, request, auth_json):
        token = get_token_from_request(request)
        try:
            _, app_token = AuthRequester().app_get_token(settings.APP_ID, settings.APP_SECRET)
            _, pin_json = AwardsRequester().get_pin(**request.data, token=token)
            _, user_json = UsersRequester().buy_pin(pin_id=pin_json['id'], user_id=auth_json['id'],
                                                    price=pin_json['price'], app_token=app_token['access'])
            return user_json
        except TypeError as e:
            return Response({'error': 'Неправильный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except UnexpectedResponse as e:
            return Response(e.body, status=e.code)
        except BaseApiRequestError:
            return Response({'error': 'Проблемы с сервисом мест, попробуйте позже'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @collect_request_stats_decorator(another_stats_funcs=[CollectStatsMixin.collect_pin_purchase_stats,
                                                          CollectStatsMixin.collect_achievement_stats])
    def post(self, request: Request):
        auth_json = self.get_user_info(request)
        if isinstance(auth_json, Response):
            return auth_json
        stats_kwargs = []
        user_json = self.buy_pin(request, auth_json)
        if isinstance(user_json, Response):
            return user_json
        stats_kwargs.append({
            'request': request,
            'pin_id': request.data['pin_id']
        })
        new_user = self.add_achievement(request, 6, auth_json)
        if new_user is not None:
            stats_kwargs.append({
                'request': request,
                'achievement_id': 6,
            })
        user_json = self.update_rating(request, 100, auth_json) or user_json
        return Response(user_json, status=status.HTTP_201_CREATED), stats_kwargs
