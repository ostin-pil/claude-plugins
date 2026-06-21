package com.acme.order;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class OrderServiceTest {
    @Test
    void status() {
        assertEquals("ok", new OrderService().status());
    }
}
