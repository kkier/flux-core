/************************************************************\
 * Copyright 2024 Lawrence Livermore National Security, LLC
 * (c.f. AUTHORS, NOTICE.LLNS, COPYING)
 *
 * This file is part of the Flux resource manager framework.
 * For details, see https://github.com/flux-framework.
 *
 * SPDX-License-Identifier: LGPL-3.0
\************************************************************/

#if HAVE_CONFIG_H
#include "config.h"
#endif
#include <jansson.h>
#include <errno.h>
#include <string.h>

#include <flux/core.h>

#include "src/common/libtap/tap.h"
#include "ccan/str/str.h"

#include "src/modules/resource/drainset.h"

static void check_drainset (struct drainset *ds,
                           const char *json_str)
{
    char *s;
    json_t *o = drainset_to_json (ds);
    json_t *expected = json_loads (json_str, 0, NULL);
    if (!o || !expected)
        BAIL_OUT ("drainset_to_json failed");
    if (!(s = json_dumps (o, JSON_COMPACT)))
        BAIL_OUT ("json_dumps failed");
    diag ("drainset_to_json = %s", s);
    diag ("expected =         %s", json_str);
    ok (json_equal (expected, o),
        "drainset_to_json got expected result");
    json_decref (expected);
    json_decref (o);
    free (s);
}

static void test_empty ()
{
    struct drainset *ds = drainset_create ();
    if (!ds)
        BAIL_OUT ("drainset_create failed");
    diag ("empty drainset should return empty JSON object");
    check_drainset (ds, "{}");
    drainset_destroy (ds);
}

static void test_basic ()
{
    struct drainset *ds = drainset_create ();
    if (!ds)
        BAIL_OUT ("drainset_create failed");

    ok (drainset_drain_rank (NULL, 0, 1234.0, NULL) < 0 && errno == EINVAL,
        "drainset_drain_rank (NULL, ...) returns EINVAL");

    for (unsigned int i = 0; i < 8; i++) {
        ok (drainset_drain_rank (ds, i, 1234.0, "test") == 0,
            "drainset_drain_rank: rank=%u", i);
    }
    check_drainset (ds,
                    "{\"0-7\":{\"timestamp\":1234.0,\"reason\":\"test\"}}");
    drainset_destroy (ds);
}

static void test_multiple ()
{
    struct drainset *ds = drainset_create ();

    if (!ds)
        BAIL_OUT ("drainset_create failed");

    ok (drainset_drain_rank (ds, 0, 1234.0, "test") == 0,
        "drainset_drain_rank: rank=0");
    ok (drainset_drain_rank (ds, 1, 2345.0, "test") == 0,
        "drainset_drain_rank: rank=1");
    ok (drainset_drain_rank (ds, 2, 1234.0, "test1") == 0,
        "drainset_drain_rank: rank=1");
    ok (drainset_drain_rank (ds, 3, 1234.0, "test") == 0,
        "drainset_drain_rank: rank=0");
    ok (drainset_drain_rank (ds, 4, 1234.0, NULL) == 0,
        "drainset_drain_rank: rank=1");

    check_drainset (ds,
                    "{\"0,3\":{\"timestamp\":1234.0,\"reason\":\"test\"},"
                    "\"1\":{\"timestamp\":2345.0,\"reason\":\"test\"},"
                    "\"2\":{\"timestamp\":1234.0,\"reason\":\"test1\"},"
                    "\"4\":{\"timestamp\":1234.0,\"reason\":\"\"}}");
    drainset_destroy (ds);
}

int main (int argc, char *argv[])
{
    plan (NO_PLAN);
    test_empty ();
    test_basic ();
    test_multiple ();
    done_testing ();
    return (0);
}


/*
 * vi:ts=4 sw=4 expandtab
 */
