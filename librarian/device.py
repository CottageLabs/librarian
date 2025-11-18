def get_device() -> str:
    """Auto-detect the best available device.

    Returns:
        'cuda' if CUDA is available, otherwise 'cpu'
    """
    try:
        import torch
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:
        return 'cpu'
