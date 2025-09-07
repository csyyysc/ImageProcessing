"""
Main UI component that combines all UI utilities
"""
from .css import apply_all_css, apply_image_container_css
from .buttons import (
    create_download_button, create_bulk_download_button, create_delete_button,
    create_transform_button, create_upload_button, create_action_buttons_layout,
    create_confirmation_buttons
)
from .metrics import (
    create_metric_row, create_image_statistics_metrics, create_download_statistics_metrics,
    create_single_metric, create_progress_bar, create_usage_indicator
)
from .sections import (
    create_sidebar_section, create_info_section, create_warning_section,
    create_error_section, create_success_section, create_expandable_section,
    create_tab_section, create_subsection, create_divider, create_spacer,
    create_status_section
)

# Re-export all components for easy importing
__all__ = [
    # CSS
    'apply_all_css',
    'apply_image_container_css',
    
    # Buttons
    'create_download_button',
    'create_bulk_download_button',
    'create_delete_button',
    'create_transform_button',
    'create_upload_button',
    'create_action_buttons_layout',
    'create_confirmation_buttons',
    
    # Metrics
    'create_metric_row',
    'create_image_statistics_metrics',
    'create_download_statistics_metrics',
    'create_single_metric',
    'create_progress_bar',
    'create_usage_indicator',
    
    # Sections
    'create_sidebar_section',
    'create_info_section',
    'create_warning_section',
    'create_error_section',
    'create_success_section',
    'create_expandable_section',
    'create_tab_section',
    'create_subsection',
    'create_divider',
    'create_spacer',
    'create_status_section',
]