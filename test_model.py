from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


class TestBatch:

    @staticmethod
    def make_batch_and_line(sku, batch_qty, line_qty):
        return (
            Batch("batch-001", sku, batch_qty, eta=date.today()),
            OrderLine("order-123", sku, line_qty)
        )

    def test_allocating_to_a_batch_reduces_the_available_quantity(self):
        batch, line = self.make_batch_and_line("SMALL TABLE", 20, 2)
        batch.allocate(line)
        assert batch.available_quantity == 18

    def test_can_allocate_if_available_greater_than_required(self):
        large_batch, small_line = self.make_batch_and_line("ELEGANT-LAMP", 20,
                                                           2)
        assert large_batch.can_allocate(small_line)

    def test_cannot_allocate_if_available_smaller_than_required(self):
        small_batch, large_line = self.make_batch_and_line("ELEGANT-LAMP", 2,
                                                           20)
        assert small_batch.can_allocate(large_line) is False

    def test_can_allocate_if_available_equal_to_required(self):
        batch, line = self.make_batch_and_line("ELEGANT-LAMP", 2, 2)
        assert batch.can_allocate(line)

    @staticmethod
    def test_cannot_allocate_if_skus_do_not_match():
        batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
        different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
        assert batch.can_allocate(different_sku_line) is False

    def test_can_only_deallocated_lines(self):
        batch, unallocated_line = self.make_batch_and_line("SMALL TABLE", 20, 2)
        batch.deallocate(unallocated_line)
        assert batch.available_quantity == 20

    def test_allocation_is_unique(self):
        batch, line = self.make_batch_and_line("SMALL TABLE", 20, 2)
        batch.allocate(line)
        new_batch, new_line = self.make_batch_and_line("SMALL TABLE", 20, 2)
        batch.allocate(new_line)
        assert batch.available_quantity == 18


class TestAllocate:

    def test_prefers_current_stock_batches_to_shipments(self):
        in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100,
                               eta=None)

        shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100,
                               eta=tomorrow)
        line = OrderLine("oref", "RETRO-CLOCK", 10)
        allocate(line, [in_stock_batch, shipment_batch])
        assert in_stock_batch.available_quantity == 90
        assert shipment_batch.available_quantity == 100

    def test_prefers_earlier_batches(self):
        earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100,
                         eta=today)

        medium = Batch("normal-batch", "MINIMALIST-SPOON", 100,
                       eta=tomorrow)
        latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
        line = OrderLine("order1", "MINIMALIST-SPOON", 10)
        allocate(line, [medium, earliest, latest])
        assert earliest.available_quantity == 90
        assert medium.available_quantity == 100
        assert latest.available_quantity == 100

    def test_returns_allocated_batch_red(self):
        in_stock_batch = Batch(
            "in-stock-batch-ref", "HIGHBROW-POSTER",
            100, eta=None
        )
        shipment_batch = Batch(
            "shipment-batch-ref", "HIGHBROW-POSTER",
            100, eta=tomorrow
        )
        line = OrderLine("oref", "HIGHBROW-POSTER", 10)
        allocation = allocate(line, [in_stock_batch, shipment_batch])
        assert allocation == in_stock_batch.reference
