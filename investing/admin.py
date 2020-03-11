from django.contrib import admin

from .models import Stock
from .models import Holding
from .models import ProfitsToAssets
from .models import ExchangeRate
from .models import Assets
from .models import Liabilities
from .models import InterestExpense
from .models import CoGS
from .models import Revenue
from .models import SGA_Expense
from .models import OperatingProfitability
from .models import SharesOutstanding
from .models import MarketCapInDollars
from .models import MarketCap
from .models import PriceToBook
from .models import Investment


class ProfitabilityInline(admin.TabularInline):
    model = ProfitsToAssets

    def has_delete_permission(self, request, obj):
        return True


class StockAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'yahoo_ticker', 'name', 'market_cap', 'p_b', 'currency', 'p']
    ordering = ['market_cap', 'p_b']
    inlines = [
        ProfitabilityInline,
    ]
    search_fields = ['ticker']


class AssetsAdmin(admin.ModelAdmin):
    list_display = ['stock', 'assets', 'year']
    ordering = ['stock', 'assets', 'year']
    search_fields = ['stock']


class LiabilitiesAdmin(admin.ModelAdmin):
    list_display = ['stock', 'liabilities', 'year']
    ordering = ['stock', 'liabilities', 'year']
    search_fields = ['stock']


class RevenueAdmin(admin.ModelAdmin):
    list_display = ['stock', 'revenue', 'year']
    ordering = ['stock', 'revenue', 'year']
    search_fields = ['stock']


class CoGSAdmin(admin.ModelAdmin):
    list_display = ['stock', 'CoGS', 'year']
    ordering = ['stock', 'CoGS', 'year']
    search_fields = ['stock']


class InterestExpAdmin(admin.ModelAdmin):
    list_display = ['stock', 'interestExpense', 'year']
    ordering = ['stock', 'interestExpense', 'year']
    search_fields = ['stock']


class SGAExpAdmin(admin.ModelAdmin):
    list_display = ['stock', 'SGA_Expense', 'year']
    ordering = ['stock', 'SGA_Expense', 'year']
    search_fields = ['stock']


class OutstandingSharesAdmin(admin.ModelAdmin):
    list_display = ['stock', 'sharesOutstanding', 'year']
    ordering = ['stock', 'sharesOutstanding', 'year']
    search_fields = ['stock']


class MarketCapAdmin(admin.ModelAdmin):
    list_display = ['stock', 'marketCap', 'year']
    ordering = ['stock', 'marketCap', 'year']
    search_fields = ['stock']


class ProfitsAdmin(admin.ModelAdmin):
    list_display = ['stock', 'profitability', 'year']
    ordering = ['stock', 'profitability', 'year']
    search_fields = ['stock']


class OPAdmin(admin.ModelAdmin):
    list_display = ['stock', 'OP', 'year']
    ordering = ['stock', 'OP', 'year']
    search_fields = ['stock']


class PBAdmin(admin.ModelAdmin):
    list_display = ['stock', 'PB', 'year']
    ordering = ['stock', 'PB', 'year']
    search_fields = ['stock']


class INVAdmin(admin.ModelAdmin):
    list_display = ['stock', 'investment', 'year']
    ordering = ['stock', 'investment', 'year']
    search_fields = ['stock']


class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'date', 'rate']
    ordering = ['currency', 'date', 'rate']


admin.site.register(Stock, StockAdmin)

admin.site.register(MarketCapInDollars, MarketCapAdmin)
admin.site.register(PriceToBook, PBAdmin)
admin.site.register(OperatingProfitability, OPAdmin)
admin.site.register(Investment, INVAdmin)

admin.site.register(Assets, AssetsAdmin)
admin.site.register(Liabilities, LiabilitiesAdmin)

admin.site.register(Revenue, RevenueAdmin)
admin.site.register(CoGS, CoGSAdmin)
admin.site.register(InterestExpense, InterestExpAdmin)
admin.site.register(SGA_Expense, SGAExpAdmin)
admin.site.register(SharesOutstanding, OutstandingSharesAdmin)
admin.site.register(MarketCap, MarketCapAdmin)

admin.site.register(ExchangeRate, ExchangeRateAdmin)

admin.site.register(Holding)
admin.site.register(ProfitsToAssets, ProfitsAdmin)

