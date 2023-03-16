"""
    Script for Data Migration (Profiler -> Komodo)
    Using Django as standalone library to use its ORM
"""
import datetime
import random
import string
import time
import os
import sys

from datetime import timedelta
from django.core.exceptions import MultipleObjectsReturned
from moneyed import Money
from typing import Any, Callable, cast, TypeVar

import psycopg2
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'komodo_backend.settings'

import django
django.setup()

from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Q
from komodo_backend.settings import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,
    SUPERUSER_EMAIL, SUPERUSER_FIRST_NAME,
    SUPERUSER_LAST_NAME, SUPERUSER_PASSWORD, DB_NAME
)
from api.constants import (
    DOMAIN_INSURANCE, DOMAIN_MARKET_DATA, DOMAIN_TECHNOLOGY, DOMAIN_TRAVEL,
    SUPPLIER_TYPE_RESELLER, SUPPLIER_TYPE_TMC, SUPPLIER_TYPE_GENERAL, DOMAINS,
    BUYER_STATUS_ACTIVE, BUYER_STATUS_INACTIVE, BUYER_STATUSES, SUPPLIER_TYPES,
    PRODUCT_STATUS_ACTIVE, CONTRACT_STATUS_ACTIVE, CONTRACT_STATUS_UPCOMING,
    CONTRACT_STATUS_EXPIRED, CONTRACT_STATUS_TERMINATED, LICENSE_PERIOD_TYPE_OTHER,
    LICENSE_PERIOD_USAGE_UNIT_OTHER, CONTRACT_DURATION_UNIT_MONTHS, CONTRACT_DURATION_UNIT_YEARS,
    SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY, SUBSCRIPTION_BILLING_FREQUENCIES
)
from api.models import (
    Employer, EmployerBusinessUnit, Geography, EmployerGeography, Department,
    EmployerDepartment, CoverageGroup, EmployerCoverageGroup, EmployeeLevel,
    EmployerEmployeeLevel, EmployerCostCenter, User, Buyer, Industry, Address,
    Supplier, Product, Person, Contact, LicensePeriod, Employee, Contract,
    Subscription, BusinessDeal, ProductType, CoverageGroupRestriction,
    DepartmentRestriction, GeographyRestriction
)

F = TypeVar("F", bound=Callable[..., Any])


# flake8: noqa: C901
def timed_function(func: F) -> F:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        print(f"Function: {func.__name__}...")
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Done in {(end - start):.2f}s\n")
        return result

    return cast(F, wrapper)


class DataMigrationHandler:

    def __init__(self) -> None:
        # Connection to Profiler DB locally (after download the latest backup from Heroku and restore it locally)
        conn = psycopg2.connect(
            f"dbname='profiler' user='{DB_USER}' password='{DB_PASSWORD}' host='{DB_HOST}' port='{DB_PORT}'"
        )
        # main cursor
        self.cursor: RealDictCursor = conn.cursor(cursor_factory=RealDictCursor)

        # verticals in profiler vs domain constant in komodo mapping
        # mapping: profiler_vertical_id: komodo_constant_id
        self.vertical_to_domain = {
            1: DOMAIN_INSURANCE,
            2: DOMAIN_MARKET_DATA,
            3: DOMAIN_TECHNOLOGY,
            4: DOMAIN_TRAVEL
        }

    @timed_function
    def clean_komodo_tables(self) -> None:
        try:
            with transaction.atomic():
                # Business tables
                Geography.objects.all().delete()
                print('Geographies deleted')
                Industry.objects.all().delete()
                print("Industries deleted")
                Address.objects.all().delete()
                print("Addresses deleted")
                Product.objects.all().delete()
                print("Products deleted")
                Contract.objects.all().delete()
                print("Contract table deleted")
                # should be deleted by cascade because Contract FK (but keep it until finish script and validations)
                Subscription.objects.all().delete()
                print("Subscription table deleted")
                # should be deleted by cascade because Subscription FK (but keep it until finish script and validations)
                LicensePeriod.objects.all().delete()
                print("SpendObligation table deleted")

                # Maintenance tables
                CoverageGroup.objects.all().delete()
                print("Coverage Groups deleted")
                Department.objects.all().delete()
                print('Departments deleted')
                EmployeeLevel.objects.all().delete()
                print("Employee Levels deleted")

                # Entities tables
                BusinessDeal.objects.all().delete()
                print("BusinessDeal table deleted")
                Buyer.objects.all().delete()
                print('Buyers deleted')
                Employer.objects.all().delete()
                print('Employers deleted')
                Supplier.objects.all().delete()
                print("Suppliers deleted")
                Person.objects.all().delete()
                print("Person table deleted")
                Contact.objects.all().delete()
                print("Contact table deleted")
                Employee.objects.all().delete()
                print("Employee table deleted")

        except Exception as ex:
            print(ex.__str__())

    @timed_function
    def process(self):
        """
        Function which call all the process functions in order for data migration
        :return:
        """
        try:
            with transaction.atomic():
                self.process_industries()
                self.process_addresses()
                self.process_employers_and_buyers()
                self.process_suppliers()
                self.process_business_units()
                self.process_cost_centers()
                self.process_coverage_groups()
                self.process_departments()
                self.process_employee_levels()
                self.process_geographies()
                self.process_products()
                self.process_subscriptions_and_contracts()
                self.process_subscriptions_and_license_periods()
                self.update_contracts_statuses()
                self.process_contacts()
                self.process_employees()

        except Exception as ex:
            print(ex.__str__())

    @timed_function
    def process_industries(self) -> None:
        self.cursor.execute("select * from industries")
        for industry_row in self.cursor.fetchall():
            industry_id = industry_row["id"]
            domain_id = self.vertical_to_domain[industry_row["vertical_id"]]
            industry_name = industry_row["name"]
            if not industry_name:
                print(f"Cannot create industry ({industry_id}), name is null")
                continue

            print(f'Industry: {industry_id}. {industry_name} (Domain: {dict(DOMAINS)[domain_id]})')
            industry, _ = Industry.objects.get_or_create(id=industry_id)
            industry.name = industry_name
            industry.domain = domain_id
            industry.save()

    @timed_function
    def process_addresses(self) -> None:
        self.cursor.execute("select * from addresses")
        for address_row in self.cursor.fetchall():
            address_id = address_row["id"]
            address_street1 = address_row["street1"] or ""
            if not address_street1:
                continue

            address_street2 = address_row["street2"] or ""
            address_city = address_row["city"] or ""
            address_state = address_row["state"] or ""
            address_country = address_row["country"] or ""
            address_postal_code = address_row["postal_code"] or ""

            print(f'Address: {address_id}. {address_street1}')
            address, _ = Address.objects.get_or_create(id=address_id)
            address.street1 = address_street1
            address.street2 = address_street2
            address.city = address_city
            address.state = address_state
            address.country = address_country
            address.postal_code = address_postal_code
            address.save()

    @timed_function
    def process_employers_and_buyers(self) -> None:
        self.cursor.execute("select * from employers order by id asc")
        for employer_row in self.cursor.fetchall():
            employer_id = employer_row["id"]
            employer_name = employer_row["name"]
            if not employer_name:
                continue

            # Employer
            employer, _ = Employer.objects.get_or_create(id=employer_id)
            employer.name = employer_name
            employer.save()

            # Buyer
            short_name = employer_row["short_name"]
            short_code = employer_row["short_code"]
            savings_report_frequency_in_months = employer_row["savings_report_frequency_in_months"]
            first_joined_at = employer_row["first_joined_at"]
            account_status = BUYER_STATUS_ACTIVE if employer_row["status"] == "active" else BUYER_STATUS_INACTIVE
            buyer = Buyer(
                id=employer_id,
                employer_id=employer_id,
                short_name=short_name,
                short_code=short_code,
                account_status=account_status,
                savings_report_frequency_in_months=savings_report_frequency_in_months,
                first_joined_at=first_joined_at,
            )
            buyer.save()
            print(f'Buyer & Employer: {employer_id}. {short_name} ({dict(BUYER_STATUSES)[account_status]})')

            # Addresses and Industries (these tables needs to be migrated before)
            self.cursor.execute(f"select * from address_employers where employer_id={employer_id}")
            for address_employer_row in self.cursor.fetchall():
                address_id = address_employer_row["address_id"]
                try:
                    address = Address.objects.get(id=address_id)
                    employer.addresses.add(address)
                except Address.DoesNotExist:
                    continue

            self.cursor.execute(f"select * from employer_industries where employer_id={employer_id}")
            for employer_industry_row in self.cursor.fetchall():
                industry_id = employer_industry_row["industry_id"]
                try:
                    industry = Industry.objects.get(id=industry_id)
                    employer.industries.add(industry)
                except Industry.DoesNotExist:
                    continue

    @timed_function
    def process_suppliers(self) -> None:
        self.cursor.execute("select * from suppliers")
        for supplier_row in self.cursor.fetchall():
            supplier_id = supplier_row["id"]
            supplier_name = supplier_row["name"]
            if not supplier_name:
                continue

            # Create Employer with same name of supplier (because db schema) id should be assigned because jumps in ids
            last_employer_id = Employer.objects.latest('id').id
            employer = Employer.objects.create(id=last_employer_id + 1, name=supplier_name)

            # SupplierType derivation
            if supplier_row["supplier_type_id"] == 11:      # Reseller in Profiler
                supplier_type_id = SUPPLIER_TYPE_RESELLER
            elif supplier_row["supplier_type_id"] == 16:    # TMC in Profiler
                supplier_type_id = SUPPLIER_TYPE_TMC
            else:
                supplier_type_id = SUPPLIER_TYPE_GENERAL

            # Supplier
            print(f'Supplier: {supplier_id}. {supplier_name} ({dict(SUPPLIER_TYPES)[supplier_type_id]})')
            Supplier.objects.get_or_create(id=supplier_id, employer=employer, type=supplier_type_id)

    @timed_function
    def process_business_units(self) -> None:
        self.cursor.execute("select * from business_units")
        for business_unit_row in self.cursor.fetchall():
            business_unit_id = business_unit_row["id"]
            business_unit_name = business_unit_row["name"] or "DEFAULT_NAME"
            business_unit_employer_id = business_unit_row["employer_id"]
            if not business_unit_employer_id:
                continue
            try:
                employer = Employer.objects.get(id=business_unit_employer_id)
            except Employer.DoesNotExist:
                continue

            print(f'Business Unit: {business_unit_id}. {business_unit_name}')
            business_unit, _ = EmployerBusinessUnit.objects.get_or_create(id=business_unit_id, employer=employer)
            business_unit.name = business_unit_name
            business_unit.save()

    @timed_function
    def process_cost_centers(self) -> None:
        self.cursor.execute("select * from cost_centers")
        for cost_center_row in self.cursor.fetchall():
            cost_center_id = cost_center_row["id"]
            cost_center_name = cost_center_row["name"] or "DEFAULT_NAME"

            cost_center_employer_id = cost_center_row["employer_id"]
            if not cost_center_employer_id:
                continue
            try:
                employer = Employer.objects.get(id=cost_center_employer_id)
            except Employer.DoesNotExist:
                continue

            print(f'Cost Center: {cost_center_id}. {cost_center_name}')
            cost_center, _ = EmployerCostCenter.objects.get_or_create(id=cost_center_id, employer=employer)
            cost_center.name = cost_center_name
            cost_center.save()

    @timed_function
    def process_coverage_groups(self) -> None:
        self.cursor.execute("select * from coverage_groups")
        for coverage_group_row in self.cursor.fetchall():
            coverage_group_name = coverage_group_row["name"] or "DEFAULT_NAME"
            coverage_group_id = coverage_group_row["id"]
            if not coverage_group_id:
                continue

            print(f'CoverageGroup: {coverage_group_id}. {coverage_group_name}')
            coverage_group, _ = CoverageGroup.objects.get_or_create(id=coverage_group_id)
            coverage_group.name = coverage_group_name
            coverage_group.save()

        # Employer Coverage Groups
        self.cursor.execute("select * from employer_coverage_groups")
        for employer_coverage_group_row in self.cursor.fetchall():
            name = employer_coverage_group_row["name"] or "DEFAULT_NAME"

            employer_coverage_group_id = employer_coverage_group_row["id"]
            if not employer_coverage_group_id:
                continue

            employer_id = employer_coverage_group_row["employer_id"]
            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                continue

            coverage_group_id = employer_coverage_group_row["coverage_group_id"]
            try:
                coverage_group = CoverageGroup.objects.get(id=coverage_group_id)
            except CoverageGroup.DoesNotExist:
                continue

            print(f'Employer CoverageGroup: {employer_coverage_group_id}. {name}')
            employer_coverage_group, _ = EmployerCoverageGroup.objects.get_or_create(
                id=employer_coverage_group_id,
                employer=employer
            )
            employer_coverage_group.name = name
            employer_coverage_group.coverage_group = coverage_group
            employer_coverage_group.save()

        # Create a corresponding employer_coverage_group for every employer where one doesn't exist
        base_employer_coverage_group_id = EmployerCoverageGroup.objects.aggregate(Max("id"))["id__max"] + 1
        for employer in Employer.objects.filter(buyer__isnull=False).distinct():
            for coverage_group in CoverageGroup.objects.all():
                if not EmployerCoverageGroup.objects.filter(employer=employer, coverage_group=coverage_group).exists():
                    employer_coverage_group = EmployerCoverageGroup(
                        id=base_employer_coverage_group_id,
                        employer=employer,
                        coverage_group=coverage_group
                    )
                    employer_coverage_group.save()
                    base_employer_coverage_group_id += 1

    @timed_function
    def process_departments(self) -> None:
        self.cursor.execute("select * from departments")
        for department_row in self.cursor.fetchall():
            name = department_row["name"] or "DEFAULT_NAME"
            department_id = department_row["id"]
            if not department_id:
                continue

            print(f'Department: {department_id}. {name}')
            deparment_obj, _ = Department.objects.get_or_create(id=department_id)
            deparment_obj.name = name
            deparment_obj.save()

        # Employer Departments
        self.cursor.execute("select * from employer_departments")
        for employer_department_row in self.cursor.fetchall():
            name = employer_department_row["name"] or "DEFAULT_NAME"
            employer_department_id = employer_department_row["id"]
            if not employer_department_id:
                continue

            employer_id = employer_department_row["employer_id"]
            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                continue

            deparment_id = employer_department_row["department_id"]
            try:
                department = Department.objects.get(id=deparment_id)
            except Department.DoesNotExist:
                continue

            print(f'Employer Department: {employer_department_id}. {name}')
            employer_department, _ = EmployerDepartment.objects.get_or_create(
                id=employer_department_id,
                employer=employer
            )
            employer_department.name = name
            employer_department.department = department
            employer_department.save()

        # Create a corresponding employer_department for every employer where one doesn't exist
        base_employer_department_id = EmployerDepartment.objects.aggregate(Max("id"))["id__max"] + 1
        for employer in Employer.objects.filter(buyer__isnull=False).distinct():
            for department in Department.objects.all():
                if not EmployerDepartment.objects.filter(employer=employer, department=department).exists():
                    employer_department = EmployerDepartment(
                        id=base_employer_department_id,
                        employer=employer,
                        department=department
                    )
                    employer_department.save()
                    base_employer_department_id += 1

    @timed_function
    def process_employee_levels(self) -> None:
        self.cursor.execute("select * from employee_levels")
        for employee_level_row in self.cursor.fetchall():
            name = employee_level_row["name"] or "DEFAULT_NAME"
            employee_level_id = employee_level_row['id']
            if not employee_level_id:
                continue

            print(f'Employee Level: {employee_level_id}. {name}')
            employee_level, _ = EmployeeLevel.objects.get_or_create(id=employee_level_id)
            employee_level.name = name
            employee_level.save()

        # Employer Employee Levels
        self.cursor.execute("select * from employer_employee_levels")
        for employer_employee_level_row in self.cursor.fetchall():
            name = employer_employee_level_row["name"] or "DEFAULT_NAME"

            employer_employee_level_id = employer_employee_level_row["id"]
            if not employer_employee_level_id:
                continue

            employer_id = employer_employee_level_row["employer_id"]
            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                continue

            employee_level_id = employer_employee_level_row["employee_level_id"]
            try:
                employee_level = EmployeeLevel.objects.get(id=employee_level_id)
            except EmployeeLevel.DoesNotExist:
                continue

            print(f'Employer EmployeeLevel: {employer_employee_level_id}. {name}')
            employer_employee_level, _ = EmployerEmployeeLevel.objects.get_or_create(
                id=employer_employee_level_id,
                employer=employer
            )
            employer_employee_level.name = name
            employer_employee_level.employee_level = employee_level
            employer_employee_level.save()

        # Create a corresponding employer_employee_level for every employer where one doesn't exist
        base_employer_employee_level_id = EmployerEmployeeLevel.objects.aggregate(Max("id"))["id__max"] + 1
        for employer in Employer.objects.filter(buyer__isnull=False).distinct():
            for employee_level in EmployeeLevel.objects.all():
                if not EmployerEmployeeLevel.objects.filter(employer=employer, employee_level=employee_level).exists():
                    employer_employee_level = EmployerEmployeeLevel(
                        id=base_employer_employee_level_id, employer=employer, employee_level=employee_level
                    )
                    employer_employee_level.save()
                    base_employer_employee_level_id += 1

    @timed_function
    def process_geographies(self) -> None:
        self.cursor.execute("select * from geographies")
        geographies = []
        geographies_rows = self.cursor.fetchall()
        for geography_row in geographies_rows:
            geography_name = geography_row["name"]
            geography_id = geography_row["id"]
            if not geography_id:
                continue

            print(f'Geography: {geography_id}. {geography_name}')
            geography, _ = Geography.objects.get_or_create(id=geography_id)
            geography.name = geography_name
            geography.save()
            geographies.append(geography)

        # Update parent_id field in geographies objs after the creation process to avoid constraint fk errors
        for geography_row in geographies_rows:
            geography_id = geography_row["id"]
            if not geography_id:
                continue

            try:
                geography = Geography.objects.get(id=geography_id)
            except Geography.DoesNotExist:
                continue

            geography_parent_id = geography_row["parent_id"]
            try:
                geography_parent = Geography.objects.get(id=geography_parent_id)
            except Geography.DoesNotExist:
                geography_parent = None

            print(f'Geography update: {geography_id}. ParentId: {geography_parent_id}')
            geography.parent = geography_parent
            geography.save()

        # Employer Geographies
        self.cursor.execute("select * from employer_geographies")
        employer_geographies_rows = self.cursor.fetchall()
        for employer_geography_row in employer_geographies_rows:
            employer_geography_name = employer_geography_row["name"]
            employer_geography_id = employer_geography_row["id"]
            if not employer_geography_id:
                continue

            employer_id = employer_geography_row["employer_id"]
            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                print(f'Employer does not exist for id: {employer_id}')
                continue

            geography_id = employer_geography_row["geography_id"]
            try:
                geography = Geography.objects.get(id=geography_id)
            except Geography.DoesNotExist:
                print(f'Geography  does not exist for id: {geography_id}')
                continue

            print(f'Employer Geography: {employer_geography_id}. {employer_geography_name}')
            employer_geography, _ = EmployerGeography.objects.get_or_create(
                id=employer_geography_id,
                employer=employer
            )
            employer_geography.name = employer_geography_name
            employer_geography.geography = geography
            employer_geography.save()

        # Update parent_id field in employer_geographies objs after the creation process to avoid constraint fk errors
        for employer_geography_row in employer_geographies_rows:
            employer_geography_id = employer_geography_row["id"]
            if not employer_geography_id:
                continue

            try:
                employer_geography = EmployerGeography.objects.get(id=employer_geography_id)
            except EmployerGeography.DoesNotExist:
                continue

            employer_geography_parent_id = employer_geography_row["parent_id"]
            try:
                employer_geography_parent = EmployerGeography.objects.get(id=employer_geography_parent_id)
            except EmployerGeography.DoesNotExist:
                employer_geography_parent = None

            print(f'EmployerGeography update: {employer_geography_id}. ParentId: {employer_geography_parent_id}')
            employer_geography.parent = employer_geography_parent
            employer_geography.save()

        # Create a corresponding employer_geography for every employer where one doesn't exist
        base_employer_geography_id = EmployerGeography.objects.aggregate(Max("id"))["id__max"] + 1
        for employer in Employer.objects.filter(buyer__isnull=False).distinct():
            for geography in geographies:
                if not EmployerGeography.objects.filter(employer=employer, geography=geography).exists():
                    parent = None
                    if geography.parent:
                        parent = EmployerGeography.objects.get(employer=employer, geography=geography.parent)
                    employer_geography = EmployerGeography(
                        id=base_employer_geography_id,
                        employer=employer,
                        geography=geography,
                        parent=parent,
                    )
                    employer_geography.save()
                    base_employer_geography_id += 1

    @timed_function
    def process_products(self) -> None:

        # default values in case null values for fk (get first objs in db)
        default_industry_instance = Industry.objects.first()
        default_supplier_instance = Supplier.objects.first()
        default_product_type_instance = ProductType.objects.first()
        default_geography_instance = Geography.objects.first()

        self.cursor.execute("select * from products")
        for product_row in self.cursor.fetchall():
            product_id = product_row["id"]
            product_description = product_row["description"] or "DEFAULT"
            product_name = product_row["name"]
            if not product_name:
                print(f"Cannot create product ({product_id}), name is null")
                continue

            product_supplier_id = product_row["supplier_id"]
            # derive the domain value from supplier associated with the product
            self.cursor.execute(f"select vertical_id from suppliers where id = {product_supplier_id}")
            supplier_row = self.cursor.fetchone()
            domain = self.vertical_to_domain[supplier_row["vertical_id"]]
            try:
                supplier = Supplier.objects.get(id=product_supplier_id)
            except:
                print(f"Warning... Supplier not found for product ({product_id}). Setting to first supplier")
                supplier = default_supplier_instance

            product_industry_id = product_row["industry_id"]
            try:
                industry = Industry.objects.get(id=product_industry_id)
            except:
                industry = default_industry_instance

            print(f'Product: {product_id}. {product_name} (Domain: {dict(DOMAINS)[domain]}')
            product, _ = Product.objects.get_or_create(id=product_id, domain=domain, supplier=supplier)
            product.name = product_name
            product.description = product_description
            product.status = PRODUCT_STATUS_ACTIVE
            product.url = ""
            product.save()

            # Many to Many fields
            product.industries.add(industry)
            product.types.add(default_product_type_instance)
            product.geographies.add(default_geography_instance)

    @timed_function
    def process_subscriptions_and_contracts(self) -> None:

        self.cursor.execute("select * from subscriptions")
        for index, subscription_row in enumerate(self.cursor.fetchall(), start=1):
            now = timezone.now()
            subscription_id = subscription_row["id"]
            subscription_start_date = subscription_row["starts_at"]
            subscription_end_date = subscription_row["ends_at"]
            subscription_autorenewal_duration = subscription_row["autorenew_duration"]
            subscription_autorenewal_duration_unit = CONTRACT_DURATION_UNIT_MONTHS if 'month' in subscription_row["autorenew_duration_unit"] else CONTRACT_DURATION_UNIT_YEARS
            subscription_autorenewal_deadline = subscription_row["autorenew_deadline"]
            subscription_terminated_at = subscription_row["terminated_at"]
            subscription_name = subscription_row["name"]
            subscription_notes = subscription_row["notes"] or ""

            subscription_product_id = subscription_row["product_id"]
            try:
                product = Product.objects.get(id=subscription_product_id)
            except Product.DoesNotExist:
                continue

            # buyer has the same id of employer based on migration above
            subscription_buyer_id = subscription_row["employer_id"]
            try:
                buyer = Buyer.objects.get(id=subscription_buyer_id)
            except Buyer.DoesNotExist:
                continue

            # try to find a Supplier based on supplier_name column in subscription table
            subscription_supplier_name = subscription_row["supplier_name"]
            try:
                supplier = Supplier.objects.get(employer__name=subscription_supplier_name)
            except MultipleObjectsReturned:
                supplier = Supplier.objects.filter(employer__name=subscription_supplier_name)[0]
            except Supplier.DoesNotExist:
                continue

            # determine BusinessDeal
            business_deal, _ = BusinessDeal.objects.get_or_create(buyer=buyer, supplier=supplier)
            print(f'BusinessDeal: {business_deal.id}. {business_deal.__str__()}')

            # # # Contract
            contract = Contract(
                business_deal=business_deal,
                buyer_entity_name=buyer.employer.name,
                start_date=subscription_start_date,
                end_date=subscription_end_date,
                autorenewal_duration=subscription_autorenewal_duration,
                autorenewal_duration_unit=subscription_autorenewal_duration_unit,
                autorenewal_deadline=subscription_autorenewal_deadline,
                terminated_at=subscription_terminated_at,
                # TODO: Check with backend if these fields will be populated after dm process
                status=CONTRACT_STATUS_ACTIVE,
                previous_contract=None,
                contract_series=None,
                created_at=now,
                updated_at=now,
            )
            contract.save()
            print(f'{index}. Contract: {contract.id}', end=' ')

            # # # Subscription
            subscription = Subscription(
                id=subscription_id,
                contract=contract,
                product=product,
                domain=product.domain,
                name=subscription_name,
                tax_rate=None,
                start_date=subscription_start_date,
                end_date=subscription_end_date,
                notes=subscription_notes,
                # new fields
                reseller_supplier=None,
                tmc_supplier=None,
                discount_type=None,
                # assign a default value to these fields but then will be calculated by its license periods
                billing_frequency=SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY,
                calculated_total_price=Money(amount=0, currency="USD"),
                created_at=now,
                updated_at=now,
            )
            subscription.save()
            print(f'Subscription: {subscription.id}. {subscription.name} ({subscription.start_date}_{subscription.end_date})')

    @timed_function
    def process_subscriptions_and_license_periods(self) -> None:

        for subscription in Subscription.objects.all():
            self.cursor.execute(
                f"""
                    select sub.*,
                           c.*,
                           curr.acronym,
                           LEAD(effective_at) OVER(
                              partition by sub.id
                                  order by c.effective_at
                           ) next_effective_at
                      from subscriptions sub
                     inner join cycles c on c.subscription_id = sub.id
                      left join currencies curr on c.currency_id = curr.id
                     where sub.id = {subscription.id}
                     order by c.effective_at asc
                    """
            )

            for subscription_cycle_row in self.cursor.fetchall():
                start_date = subscription_cycle_row["effective_at"]
                end_date = subscription.end_date if subscription_cycle_row["next_effective_at"] is None else subscription_cycle_row["next_effective_at"] - timedelta(days=1)
                max_credits = subscription_cycle_row["max_credits"]
                max_users = subscription_cycle_row["max_users"]
                usage_unit_price = subscription_cycle_row["usage_unit_cost"] or 0
                license_type = LICENSE_PERIOD_TYPE_OTHER if subscription_cycle_row["license_type"] is None or subscription_cycle_row["license_type"] == 0 else subscription_cycle_row["license_type"]
                usage_unit = LICENSE_PERIOD_USAGE_UNIT_OTHER if subscription_cycle_row["usage_units"] is None or subscription_cycle_row["usage_units"] == 0 else subscription_cycle_row["usage_units"]
                price = subscription_cycle_row["total_cost"] or 0
                incremental_user_price = subscription_cycle_row["incremental_user_price"] or 0
                exchange_rate_to_usd_at_time_of_purchase = subscription_cycle_row["usd_exchange_rate"]

                # License Period instead SpendObligation
                license_period = LicensePeriod(
                    subscription=subscription,
                    type=license_type,
                    price=price,
                    calculated_total_price=0,
                    exchange_rate_to_usd_at_time_of_purchase=exchange_rate_to_usd_at_time_of_purchase,
                    start_date=start_date,
                    end_date=end_date,
                    max_credits=max_credits,
                    max_users=max_users,
                    incremental_user_price=incremental_user_price,
                    usage_unit_price=usage_unit_price,
                    usage_unit=usage_unit
                )
                license_period.save()
                print(f'LicensePeriod: {license_period.id}. {license_period.get_type_display()} ({start_date} - {end_date})')

                # update subscription billing freqeuncy from lp
                try:
                    billing_frequency = [x[0] for x in SUBSCRIPTION_BILLING_FREQUENCIES if subscription_cycle_row["billing_frequency"].title() == x[1]][0]
                except:
                    # default annually
                    billing_frequency = SUBSCRIPTION_BILLING_FREQUENCY_ANNUALLY

                subscription.billing_frequency = billing_frequency
                subscription.save()

            # # # Restrictions
            self.cursor.execute(f"select * from coverage_group_restrictions where subscription_id = {subscription.id}")
            for coverage_group_restriction_row in self.cursor.fetchall():
                employer_coverage_group_id = coverage_group_restriction_row["employer_coverage_group_id"]
                try:
                    employer_coverage_group = EmployerCoverageGroup.objects.get(id=employer_coverage_group_id)
                    coverage_group_restriction = CoverageGroupRestriction(
                        employer_coverage_group=employer_coverage_group,
                        subscription=subscription
                    )
                    coverage_group_restriction.save()
                    print(f'CoverageGroupRestriction: {coverage_group_restriction.id}')
                except:
                    pass

            self.cursor.execute(f"select * from department_restrictions where subscription_id = {subscription.id}")
            for department_restriction_row in self.cursor.fetchall():
                employer_department_id = department_restriction_row["employer_department_id"]
                try:
                    employer_department = EmployerDepartment.objects.get(id=employer_department_id)
                    department_restriction = DepartmentRestriction(
                        employer_department=employer_department,
                        subscription=subscription
                    )
                    department_restriction.save()
                    print(f'DepartmentRestriction: {department_restriction.id}')
                except:
                    pass

            self.cursor.execute(f"select * from geography_restrictions where subscription_id = {subscription.id}")
            for geography_restriction_row in self.cursor.fetchall():
                employer_geography_id = geography_restriction_row["employer_geography_id"]
                try:
                    employer_geography = EmployerGeography.objects.get(id=employer_geography_id)
                    geography_restriction = GeographyRestriction(
                        employer_geography=employer_geography,
                        subscription=subscription
                    )
                    geography_restriction.save()
                    print(f'GeographyRestriction: {geography_restriction.id}')
                except:
                    pass

    @timed_function
    def update_contracts_statuses(self) -> None:
        today = datetime.datetime.now().today()

        # Active
        Contract.objects.filter(
            Q(end_date__gte=today) |
            Q(end_date__isnull=True),
            start_date__lte=today
        ).update(
            status=CONTRACT_STATUS_ACTIVE
        )
        print(f'Contracts updated -> ACTIVE')

        # Upcoming
        Contract.objects.filter(
            start_date__gt=today
        ).update(
            status=CONTRACT_STATUS_UPCOMING
        )
        print(f'Contracts updated -> UPCOMING')

        # Expired
        Contract.objects.filter(
            Q(end_date__isnull=True) |
            Q(end_date__lt=today),
            terminated_at__isnull=True
        ).update(
            status=CONTRACT_STATUS_EXPIRED
        )
        print(f'Contracts updated -> EXPIRED')

        # Terminated
        Contract.objects.filter(
            terminated_at__isnull=False
        ).update(
            status=CONTRACT_STATUS_TERMINATED
        )
        print(f'Contracts updated -> TERMINATED')

    @timed_function
    def process_contacts(self) -> None:
        self.cursor.execute("select * from contacts")
        for contact_row in self.cursor.fetchall():
            contact_id = contact_row["id"]
            email = contact_row["email"] or "".join(random.choices(string.ascii_lowercase, k=8))
            first_name = contact_row["first_name"] or "DEFAULT"
            last_name = contact_row["last_name"] or "DEFAULT"
            phone_number = contact_row["phone"]
            job_title = contact_row["title"]

            print(f'Contact: {contact_id}. {first_name} {last_name} (Email: {email})')
            # Derive Employer using contactable_type and contactable_id
            contactable_id = contact_row["contactable_id"]
            contactable_type = contact_row["contactable_type"]

            subscription = None
            # contactable_type == 'Subscription' -> employer_id from Subscription
            if contactable_type == "Subscription":
                try:
                    subscription = Subscription.objects.get(id=contactable_id)
                    employer = subscription.contract.business_deal.buyer.employer
                except:
                    continue
            # contactable_type == 'Employer' -> employer_id from the contactable_id (because is already the employer)
            elif contactable_type == "Employer":
                try:
                    employer = Employer.objects.get(id=contactable_id)
                except:
                    continue
            # contactable_type == 'TravelAgencyEnrollment' or other -> not migrate
            else:
                continue

            # Person instance
            if Person.objects.filter(email=email).exists():
                person = Person.objects.get(email=email)
                if not person.employer and employer:
                    person.employer = employer
                if person.first_name == "DEFAULT" and first_name != "DEFAULT":
                    person.first_name = first_name
                if person.last_name == "DEFAULT" and last_name != "DEFAULT":
                    person.last_name = last_name
                if not person.phone_number and phone_number != "":
                    person.phone_number = phone_number
                if not person.job_title and job_title != "":
                    person.job_title = job_title
            else:
                person = Person(
                    id=Person.objects.latest('id').id + 1,
                    email=email,
                    employer=employer,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    job_title=job_title,
                )
            person.save()

            # Contact instance
            contact, _ = Contact.objects.get_or_create(person=person)

            # Add the Contact to the Subscription to which it belongs to
            if subscription:
                subscription.contacts.add(contact)

    @timed_function
    def process_employees(self) -> None:
        self.cursor.execute("select * from users")
        for user_row in self.cursor.fetchall():
            email = user_row["email"]
            if not email:
                continue

            employer_id = user_row["employer_id"]
            if not employer_id:
                continue

            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                continue

            first_name = user_row["firstname"] or "DEFAULT"
            last_name = user_row["lastname"] or "DEFAULT"
            phone_number = user_row["phone_number"] or ""
            job_title = user_row["job_title"] or ""
            hire_date = user_row["hire_date"]
            termination_date = user_row["terminate_date"]

            if Person.objects.filter(email=email).exists():
                person = Person.objects.get(email=email)
                if not person.employer and employer:
                    person.employer = employer
                if person.first_name == "DEFAULT" and first_name != "DEFAULT":
                    person.first_name = first_name
                if person.last_name == "DEFAULT" and last_name != "DEFAULT":
                    person.last_name = last_name
                if not person.phone_number and phone_number != "":
                    person.phone_number = phone_number
                if not person.job_title and job_title != "":
                    person.job_title = job_title
                if not person.hire_date and hire_date != "":
                    person.hire_date = hire_date
                if not person.termination_date and termination_date != "":
                    person.termination_date = termination_date
            else:
                person = Person(
                    id=Person.objects.latest('id').id + 1,
                    email=email,
                    employer=employer,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    job_title=job_title,
                    hire_date=hire_date,
                    termination_date=termination_date
                )
            person.save()

            # Relationships
            business_unit_id = user_row["business_unit_id"]
            if business_unit_id:
                try:
                    business_unit = EmployerBusinessUnit.objects.get(id=business_unit_id)
                except EmployerBusinessUnit:
                    business_unit = None
            else:
                business_unit = None

            cost_center_id = user_row["cost_center_id"]
            if cost_center_id:
                try:
                    cost_center = EmployerCostCenter.objects.get(id=cost_center_id)
                except EmployerCostCenter.DoesNotExist:
                    cost_center = None
            else:
                cost_center = None

            employer_coverage_group_id = user_row["employer_coverage_group_id"]
            if employer_coverage_group_id:
                try:
                    employer_coverage_group = EmployerCoverageGroup.objects.get(id=employer_coverage_group_id)
                except EmployerCoverageGroup.DoesNotExist:
                    employer_coverage_group = None
            else:
                employer_coverage_group = None

            employer_department_id = user_row["employer_department_id"]
            if employer_department_id:
                try:
                    employer_department = EmployerDepartment.objects.get(id=employer_department_id)
                except EmployerDepartment.DoesNotExist:
                    employer_department = None
            else:
                employer_department = None

            employer_employee_level_id = user_row["employer_employee_level_id"]
            if employer_employee_level_id:
                try:
                    employer_employee_level = EmployerEmployeeLevel.objects.get(id=employer_employee_level_id)
                except EmployerEmployeeLevel.DoesNotExist:
                    employer_employee_level = None
            else:
                employer_employee_level = None

            employer_geography_id = user_row["employer_geography_id"]
            if employer_geography_id:
                try:
                    employer_geography = EmployerGeography.objects.get(id=employer_geography_id)
                except EmployerGeography.DoesNotExist:
                    employer_geography = None
            else:
                employer_geography = None

            # Create Employee and its attributes (i.e. EmployerBusinessUnit, EmployerCostCenter,
            # EmployerEmployeeLevel, EmployerCoverageGroup, EmployerDepartment, and EmployerGeography)
            employee = Employee(
                id=person.id,
                person=person,
                employer_business_unit=business_unit,
                employer_cost_center=cost_center,
                employer_coverage_group=employer_coverage_group,
                employer_department=employer_department,
                employer_employee_level=employer_employee_level,
                employer_geography=employer_geography,
            )
            employee.save()
            print(f'Employee: {employee.id}. {person.first_name} {person.last_name} (Email: {person.email})')


if __name__ == '__main__':

    # Added this validation here just in case someone runs the script by mistake in other environment != UAT-1B
    if DB_NAME == 'komodo_uat_1b':
        print("DATA MIGRATION SERVICE - STARTED\n")
        # handler
        data_migration_handler = DataMigrationHandler()

        # cleaning tables
        print("Cleaning Tables")
        data_migration_handler.clean_komodo_tables()

        # Create Superuser before to start migration to avoid later issue with Person record
        if not User.objects.filter(is_superuser=True).exists():
            print(f"Creating Superuser...", end=' ')
            user = User.objects.create_superuser(
                email=SUPERUSER_EMAIL,
                password=SUPERUSER_PASSWORD,
                first_name=SUPERUSER_FIRST_NAME,
                last_name=SUPERUSER_LAST_NAME,
            )
            print(f"Done! ({user})")

        # dm process
        print("Data Migration Process")
        data_migration_handler.process()

        print("\nDATA MIGRATION SERVICE - COMPLETED")
