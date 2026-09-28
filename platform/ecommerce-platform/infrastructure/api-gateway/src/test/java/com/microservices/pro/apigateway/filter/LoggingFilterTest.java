package com.microservices.pro.apigateway.filter;

import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.core.Ordered;
import org.springframework.http.HttpMethod;
import org.springframework.mock.http.server.reactive.MockServerHttpRequest;
import org.springframework.mock.web.server.MockServerWebExchange;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.net.InetSocketAddress;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class LoggingFilterTest {

    private final LoggingFilter filter = new LoggingFilter();

    private MockServerWebExchange exchange() {
        return MockServerWebExchange.from(MockServerHttpRequest
                .get("/api/v1/products")
                .remoteAddress(new InetSocketAddress("127.0.0.1", 54321))
                .build());
    }

    private GatewayFilterChain chainReturningEmpty() {
        GatewayFilterChain chain = mock(GatewayFilterChain.class);
        when(chain.filter(any(ServerWebExchange.class))).thenReturn(Mono.empty());
        return chain;
    }

    @Test
    void getOrderShouldRunAtHighestPrecedence() {
        assertThat(filter.getOrder()).isEqualTo(Ordered.HIGHEST_PRECEDENCE);
    }

    @Test
    void filterShouldForwardTheExchangeToTheNextChain() {
        MockServerWebExchange exchange = exchange();
        GatewayFilterChain chain = chainReturningEmpty();

        filter.filter(exchange, chain).block();

        verify(chain, times(1)).filter(exchange);
    }

    @Test
    void filterShouldNotMutateTheRequestOnItsWayThrough() {
        MockServerWebExchange exchange = exchange();
        GatewayFilterChain chain = chainReturningEmpty();

        filter.filter(exchange, chain).block();

        ArgumentCaptor<ServerWebExchange> forwarded = ArgumentCaptor.forClass(ServerWebExchange.class);
        verify(chain).filter(forwarded.capture());
        assertThat(forwarded.getValue().getRequest().getMethod()).isEqualTo(HttpMethod.GET);
        assertThat(forwarded.getValue().getRequest().getURI().getPath()).isEqualTo("/api/v1/products");
    }
}
