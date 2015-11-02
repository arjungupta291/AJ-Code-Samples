package com.tttapi.start;

import com.tttapi.start.resources.PlayGameResource;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.QueryParam;
import javax.ws.rs.PathParam;
import javax.ws.rs.core.MediaType;
import java.util.concurrent.atomic.AtomicLong;
import io.dropwizard.Application;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

public class TicTacToeAPIApplication extends Application<TicTacToeAPIConfiguration> {

    public static void main(final String[] args) throws Exception {
        new TicTacToeAPIApplication().run(args);
    }

    @Override
    public String getName() {
        return "TicTacToeAPI";
    }

    @Override
    public void initialize(final Bootstrap<TicTacToeAPIConfiguration> bootstrap) {
        // TODO: application initialization
    }

    @Override
    public void run(final TicTacToeAPIConfiguration configuration,
                    final Environment environment) {
        environment.jersey().register(new PlayGameResource());
    }

}
