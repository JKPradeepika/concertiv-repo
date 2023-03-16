import datetime
from typing import Callable, Optional

from django.utils import timezone
import pytest

from api.constants import CONTRACT_DURATION_UNIT_YEARS
from api.models.BusinessDeal import BusinessDeal
from api.models.Contract import Contract
from api.models.ContractSeries import ContractSeries

TypeContractFactory = Callable[..., Contract]


@pytest.fixture
def contract_factory(business_deal: BusinessDeal) -> TypeContractFactory:
    thirteen_months_ago = (timezone.now() - datetime.timedelta(days=395)).date()
    ten_months_from_now = (timezone.now() + datetime.timedelta(days=305)).date()

    # Closure
    def create_contract(
        business_deal: BusinessDeal = business_deal,
        buyer_entity_name: str = business_deal.buyer.employer.name,
        signed_date: datetime.date = thirteen_months_ago,
        autorenewal_duration: int = 1,
        autorenewal_duration_unit: int = CONTRACT_DURATION_UNIT_YEARS,
        autorenewal_deadline: datetime.date = ten_months_from_now,
        terminated_at: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        previous_contract: Optional[Contract] = None,
    ) -> Contract:
        contract_series = None
        if previous_contract:
            if previous_contract.contract_series:
                contract_series = previous_contract.contract_series
            else:
                contract_series = ContractSeries.objects.create()
                previous_contract.contract_series = contract_series
                previous_contract.save()

        return Contract.objects.create(
            business_deal=business_deal,
            buyer_entity_name=buyer_entity_name,
            signed_date=signed_date,
            autorenewal_duration=autorenewal_duration,
            autorenewal_duration_unit=autorenewal_duration_unit,
            autorenewal_deadline=autorenewal_deadline,
            terminated_at=terminated_at,
            start_date=start_date,
            end_date=end_date,
            previous_contract=previous_contract,
            contract_series=contract_series,
        )

    return create_contract


@pytest.fixture
def contract(contract_factory: TypeContractFactory) -> Contract:
    return contract_factory()
