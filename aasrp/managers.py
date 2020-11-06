# -*- coding: utf-8 -*-

"""
SRP Manager
"""

import logging

import requests

from django.contrib.auth.models import User

from aasrp.models import AaSrpRequest, AaSrpRequestStatus

from allianceauth import NAME
from allianceauth.eveonline.providers import provider

logger = logging.getLogger(__name__)


class AaSrpManager:
    """
    AaSrpManager
    """

    @staticmethod
    def get_kill_id(killboard_link):
        """
        get killmail ID from zKillboard link
        :param killboard_link:
        :return:
        """

        num_set = "0123456789"
        kill_id = "".join([c for c in killboard_link if c in num_set])

        return kill_id

    @staticmethod
    def get_kill_data(kill_id):
        """
        get kill data from zKillboard
        :param kill_id:
        :return:
        """

        url = "https://zkillboard.com/api/killID/%s/" % kill_id

        headers = {
            "User-Agent": NAME,
            "Content-Type": "application/json",
        }

        request_result = requests.get(url, headers=headers)
        result = request_result.json()[0]

        if result:
            killmail_id = result["killmail_id"]
            killmail_hash = result["zkb"]["hash"]

            esi_client = provider.client

            esi_killmail = esi_client.Killmails.get_killmails_killmail_id_killmail_hash(
                killmail_id=killmail_id, killmail_hash=killmail_hash
            ).result()
        else:
            raise ValueError("Invalid Kill ID")

        if esi_killmail:
            ship_type = esi_killmail["victim"]["ship_type_id"]
            logger.debug("Ship type for kill ID %s is %s" % (kill_id, ship_type))
            ship_value = result["zkb"]["totalValue"]

            logger.debug(
                "Total loss value for kill id %s is %s" % (kill_id, ship_value)
            )

            victim_id = esi_killmail["victim"]["character_id"]

            return ship_type, ship_value, victim_id

        raise ValueError("Invalid Kill ID or Hash.")

    @staticmethod
    def pending_requests_count_for_user(user: User):
        """
        returns the number of open SRP requests for given user
        or None if user has no permission
        """

        if user.has_perm("aasrp.manage_srp") or user.has_perm(
            "aasrp.manage_srp_requests"
        ):
            return AaSrpRequest.objects.filter(
                request_status=AaSrpRequestStatus.PENDING
            ).count()

        return None