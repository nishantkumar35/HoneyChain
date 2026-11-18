from django.contrib import admin
from .models import HoneyBatch, BlockchainRecord


class BlockchainRecordInline(admin.StackedInline):
    model = BlockchainRecord
    can_delete = False
    readonly_fields = ('transaction_hash', 'block_number', 'blockchain_hash',
                       'verification_status', 'registered_at')


@admin.register(HoneyBatch)
class HoneyBatchAdmin(admin.ModelAdmin):
    list_display  = ('batch_id', 'beekeeper', 'apiary', 'honey_source', 'status',
                     'quantity', 'harvest_date', 'is_registered_on_blockchain')
    list_filter   = ('status', 'honey_source', 'is_registered_on_blockchain')
    search_fields = ('batch_id', 'beekeeper__username', 'apiary__name', 'location')
    readonly_fields = ('batch_id', 'data_hash', 'qr_code', 'created_at', 'updated_at')
    inlines = [BlockchainRecordInline]


@admin.register(BlockchainRecord)
class BlockchainRecordAdmin(admin.ModelAdmin):
    list_display  = ('honey_batch', 'verification_status', 'block_number', 'registered_at')
    list_filter   = ('verification_status',)
    readonly_fields = ('honey_batch', 'transaction_hash', 'block_number',
                       'blockchain_hash', 'verification_status', 'registered_at')

