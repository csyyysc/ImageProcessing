"""
Metrics display components for Streamlit frontend
"""
import logging
import streamlit as st
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def create_metric_row(metrics: List[Dict[str, str]], columns: int = 4) -> None:
    """
    Create a row of metrics with consistent styling

    Args:
        metrics: List of metric configurations
        columns: Number of columns for metrics
    """
    if not metrics:
        return

    try:
        cols = st.columns(columns)

        for i, metric in enumerate(metrics):
            col_index = i % columns
            with cols[col_index]:
                st.metric(
                    metric.get('label', 'Metric'),
                    metric.get('value', '0'),
                    metric.get('delta', None)
                )
    except Exception as e:
        logger.error(f"Error creating metric row: {e}")


def create_image_statistics_metrics(
    total_count: int,
    total_size: int,
    avg_size: int,
    storage_used: int
) -> None:
    """
    Create image statistics metrics display

    Args:
        total_count: Total number of images
        total_size: Total size in bytes
        avg_size: Average size in bytes
        storage_used: Storage used in bytes
    """
    try:
        metrics = [
            {
                'label': 'Total Images',
                'value': str(total_count)
            },
            {
                'label': 'Total Size',
                'value': f"{total_size / (1024*1024):.1f} MB"
            },
            {
                'label': 'Average Size',
                'value': f"{avg_size / 1024:.1f} KB"
            },
            {
                'label': 'Storage Used',
                'value': f"{storage_used / (1024*1024):.1f} MB"
            }
        ]

        create_metric_row(metrics, 4)
    except Exception as e:
        logger.error(f"Error creating image statistics metrics: {e}")


def create_download_statistics_metrics(
    api_remaining: int,
    api_limit: int,
    downloads_remaining: int,
    downloads_limit: int
) -> None:
    """
    Create download statistics metrics display

    Args:
        api_remaining: Remaining API calls
        api_limit: API call limit
        downloads_remaining: Remaining downloads
        downloads_limit: Download limit
    """
    try:
        metrics = [
            {
                'label': 'API Calls Remaining',
                'value': f"{api_remaining}/{api_limit}"
            },
            {
                'label': 'Downloads Remaining',
                'value': f"{downloads_remaining}/{downloads_limit}"
            }
        ]

        create_metric_row(metrics, 2)
    except Exception as e:
        logger.error(f"Error creating download statistics metrics: {e}")


def create_single_metric(
    label: str,
    value: str,
    delta: Optional[str] = None
) -> None:
    """
    Create a single metric display

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
    """
    try:
        truncated_label = label if len(label) <= 20 else label[:17] + "..."
        st.metric(truncated_label, value, delta)
    except Exception as e:
        logger.error(f"Error creating single metric: {e}")


def create_progress_bar(
    current: int,
    total: int,
    label: str = "Progress"
) -> None:
    """
    Create a progress bar

    Args:
        current: Current value
        total: Total value
        label: Progress bar label
    """
    try:
        if total > 0:
            progress = current / total
            st.progress(progress)
            st.caption(f"{label}: {current}/{total} ({progress:.1%})")
        else:
            st.progress(0)
            st.caption(f"{label}: {current}/{total}")
    except Exception as e:
        logger.error(f"Error creating progress bar: {e}")


def create_usage_indicator(
    used: int,
    limit: int,
    label: str = "Usage"
) -> None:
    """
    Create a usage indicator with color coding

    Args:
        used: Used amount
        limit: Limit amount
        label: Indicator label
    """
    try:
        if limit > 0:
            percentage = used / limit

            # Color coding based on usage
            if percentage >= 0.9:
                color = "red"
            elif percentage >= 0.7:
                color = "orange"
            else:
                color = "green"

            st.metric(
                label,
                f"{used}/{limit}",
                f"{percentage:.1%}"
            )

            # Add color indicator
            st.markdown(f"""
            <div style="background-color: {color}; height: 4px; border-radius: 2px; margin-top: 5px;"></div>
            """, unsafe_allow_html=True)
        else:
            st.metric(label, f"{used}/{limit}")
    except Exception as e:
        logger.error(f"Error creating usage indicator: {e}")
