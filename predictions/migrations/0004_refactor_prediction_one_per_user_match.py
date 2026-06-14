from django.db import migrations


def keep_one_prediction_per_user_and_match(apps, schema_editor):
    """
    Existing data may contain one prediction per user, group and match.

    The new design stores one prediction per user and match. Before removing
    the group field, this migration keeps the most recently updated prediction
    for each user/match pair and deletes the older duplicates.
    """

    Prediction = apps.get_model("predictions", "Prediction")

    seen_prediction_keys = set()
    prediction_ids_to_delete = []

    predictions = Prediction.objects.all().order_by(
        "user_id",
        "match_id",
        "-updated_at",
        "-submitted_at",
        "-id",
    )

    for prediction in predictions:
        key = (prediction.user_id, prediction.match_id)

        if key in seen_prediction_keys:
            prediction_ids_to_delete.append(prediction.id)
        else:
            seen_prediction_keys.add(key)

    if prediction_ids_to_delete:
        Prediction.objects.filter(id__in=prediction_ids_to_delete).delete()


def reverse_migration(apps, schema_editor):
    """
    This migration removes duplicate rows and removes the group field.

    The deleted duplicate prediction rows cannot be recreated safely, so the
    reverse operation intentionally does nothing.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("predictions", "0003_match_away_score_match_external_match_id_and_more"),
    ]

    operations = [
        migrations.RunPython(
            keep_one_prediction_per_user_and_match,
            reverse_migration,
        ),
        migrations.AlterUniqueTogether(
            name="prediction",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="prediction",
            name="group",
        ),
        migrations.AlterUniqueTogether(
            name="prediction",
            unique_together={("user", "match")},
        ),
    ]