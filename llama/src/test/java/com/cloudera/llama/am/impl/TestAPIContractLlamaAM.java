/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.cloudera.llama.am.impl;

import com.cloudera.llama.am.AssertUtils;
import com.cloudera.llama.am.api.LlamaAM;
import com.cloudera.llama.am.api.LlamaAMException;
import com.cloudera.llama.am.api.LlamaAMListener;
import com.cloudera.llama.am.api.PlacedReservation;
import com.cloudera.llama.am.api.Reservation;
import com.cloudera.llama.am.api.Resource;
import com.cloudera.llama.am.api.TestReservation;
import com.cloudera.llama.util.UUID;
import org.apache.hadoop.conf.Configuration;
import org.junit.Assert;
import org.junit.Test;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;

public class TestAPIContractLlamaAM {

  public static class MyRMLlamaAMConnector extends LlamaAM {
    static boolean nullOnReserve;

    private boolean running;

    public MyRMLlamaAMConnector() {
      super(new Configuration(false));
      nullOnReserve = false;
    }

    @Override
    public void addListener(LlamaAMListener listener) {
    }

    @Override
    public void removeListener(LlamaAMListener listener) {
    }

    @Override
    public void start() throws LlamaAMException {
      running = true;
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<String> getNodes() throws LlamaAMException {
      return Collections.EMPTY_LIST;
    }

    @Override
    public synchronized void stop() {
      running = false;
    }

    @Override
    public boolean isRunning() {
      return running;
    }

    @Override
    public PlacedReservation reserve(UUID reservationId,
        Reservation reservation)
        throws LlamaAMException {
      return new PlacedReservationImpl(UUID.randomUUID(), createReservation());
    }

    @Override
    public PlacedReservation releaseReservation(UUID reservationId)
        throws LlamaAMException {
      return null;
    }

    @Override
    public PlacedReservation getReservation(UUID reservationId)
        throws LlamaAMException {
      return null;
    }

    @Override
    public List<PlacedReservation> releaseReservationsForHandle(UUID handle)
        throws LlamaAMException {
      return null;
    }
  }

  public static Reservation createReservation() {
    List<Resource> resources = new ArrayList<Resource>();
    resources.add(TestReservation.createResource());
    return new Reservation(UUID.randomUUID(), "q", resources, false);
  }

  private LlamaAM createLlamaAM() throws Exception {
    MyRMLlamaAMConnector am = new MyRMLlamaAMConnector();
    return new APIContractLlamaAM(am);
  }


  @Test(expected = IllegalArgumentException.class)
  public void testNullReservation() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.reserve(null);
    } finally {
      am.stop();
    }
  }

  @Test
  public void testIsRunning() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      Assert.assertTrue(am.isRunning());
    } finally {
      am.stop();
    }
  }

  @Test
  public void testReserveOK() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      Assert.assertNotNull(am.reserve(createReservation()));
    } finally {
      am.stop();
    }
  }

  @Test(expected = IllegalArgumentException.class)
  public void testReleaseNull() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.releaseReservation(null);
    } finally {
      am.stop();
    }
  }

  @Test
  public void testReleaseOK() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.releaseReservation(UUID.randomUUID());
    } finally {
      am.stop();
    }
  }

  @Test(expected = IllegalArgumentException.class)
  public void testGetReservationNull() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.getReservation(null);
    } finally {
      am.stop();
    }
  }

  @Test
  public void testGetReservationUnknown() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.getReservation(UUID.randomUUID());
    } finally {
      am.stop();
    }
  }

  @Test(expected = IllegalArgumentException.class)
  public void testReserveNull1() throws Exception {
    LlamaAM am = createLlamaAM();
    MyRMLlamaAMConnector.nullOnReserve = true;
    try {
      am.start();
      am.reserve(null, createReservation());
    } finally {
      am.stop();
    }
  }

  @Test(expected = IllegalArgumentException.class)
  public void testReserveNull2() throws Exception {
    LlamaAM am = createLlamaAM();
    MyRMLlamaAMConnector.nullOnReserve = true;
    try {
      am.start();
      am.reserve(UUID.randomUUID(), null);
    } finally {
      am.stop();
    }
  }


  @Test(expected = IllegalStateException.class)
  public void testDoubleStart() throws Exception {
    LlamaAM am = createLlamaAM();
    try {
      am.start();
      am.start();
    } finally {
      am.stop();
    }
  }

  @Test
  public void testMethodsPostClose() throws Exception {
    final LlamaAM am = createLlamaAM();
    am.start();
    am.stop();
    am.getConf();
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.removeListener(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.addListener(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.reserve(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.releaseReservation(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.releaseReservationsForHandle(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.getReservation(null);
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.getNodes();
        return null;
      }
    }, IllegalStateException.class);
    AssertUtils.assertException(new Callable<Object>() {
      @Override
      public Object call() throws Exception {
        am.start();
        return null;
      }
    }, IllegalStateException.class);
  }

}
