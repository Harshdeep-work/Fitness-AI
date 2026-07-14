#!/bin/bash

# Quick Start Script for QLoRA Fine-Tuning
# ==========================================
# This script helps you prepare everything for cloud GPU training

set -e

echo "=============================================="
echo "QLoRA Fine-Tuning Quick Start"
echo "=============================================="
echo ""

# Check if dataset exists
if [ ! -f "datasets/indian_diet_finetune.jsonl" ]; then
    echo "❌ Training dataset not found!"
    echo "Creating dataset now..."
    cd datasets
    python3 create_finetune_dataset.py
    cd ..
else
    echo "✅ Training dataset found"
    DATASET_SIZE=$(wc -l < datasets/indian_diet_finetune.jsonl)
    echo "   Size: $DATASET_SIZE examples"
fi

echo ""
echo "=============================================="
echo "Files Ready for Upload to Cloud GPU"
echo "=============================================="
echo ""

# Create upload directory
UPLOAD_DIR="finetune_upload"
mkdir -p $UPLOAD_DIR

# Copy necessary files
echo "📦 Copying files to $UPLOAD_DIR/..."
cp datasets/indian_diet_finetune.jsonl $UPLOAD_DIR/
cp datasets/indian_diet_test.jsonl $UPLOAD_DIR/
cp models/train_qlora.py $UPLOAD_DIR/
cp models/inference.py $UPLOAD_DIR/
cp models/compare_models.py $UPLOAD_DIR/
cp models/finetune_requirements.txt $UPLOAD_DIR/
cp models/colab_finetune.py $UPLOAD_DIR/

echo "✅ All files copied to $UPLOAD_DIR/"
echo ""

# Create a README in upload directory
cat > $UPLOAD_DIR/README.txt << 'EOF'
QLoRA Fine-Tuning Files
========================

Upload these files to your cloud GPU platform:

For Google Colab:
1. Open https://colab.research.google.com/
2. Upload colab_finetune.py
3. Change runtime to T4 GPU
4. Upload indian_diet_finetune.jsonl when prompted
5. Run all cells

For Kaggle/RunPod/Vast.ai:
1. Upload all files
2. Install: pip install -r finetune_requirements.txt
3. Train: python train_qlora.py
4. Test: python inference.py
5. Compare: python compare_models.py

Files included:
- indian_diet_finetune.jsonl (training data)
- indian_diet_test.jsonl (test data)
- train_qlora.py (main training script)
- inference.py (testing script)
- compare_models.py (comparison script)
- finetune_requirements.txt (dependencies)
- colab_finetune.py (Colab notebook)

Documentation: See models/README.md in main project
EOF

echo "📋 Created README.txt in upload directory"
echo ""

# Show file sizes
echo "=============================================="
echo "File Sizes"
echo "=============================================="
echo ""
ls -lh $UPLOAD_DIR/ | tail -n +2 | awk '{printf "%-40s %10s\n", $9, $5}'

echo ""
echo "=============================================="
echo "Next Steps"
echo "=============================================="
echo ""
echo "1️⃣  Choose a cloud GPU platform:"
echo "   • Kaggle (FREE, 30 hrs/week): https://kaggle.com"
echo "   • Google Colab Pro (\$10/month): https://colab.research.google.com"
echo "   • RunPod (\$0.34/hr): https://runpod.io"
echo "   • Vast.ai (\$0.25/hr): https://vast.ai"
echo ""
echo "2️⃣  Upload files from: ./$UPLOAD_DIR/"
echo ""
echo "3️⃣  Follow the guide:"
echo "   • Quick: models/colab_finetune.py (for Colab)"
echo "   • Detailed: models/README.md"
echo ""
echo "4️⃣  Training time: 2-4 hours"
echo ""
echo "5️⃣  Cost estimate: \$0-2"
echo ""
echo "=============================================="
echo "Documentation"
echo "=============================================="
echo ""
echo "📖 Read before training:"
echo "   • models/README.md - Complete guide"
echo "   • docs/qlora_finetuning_summary.md - Overview"
echo "   • models/DEPLOYMENT_GUIDE.md - Deployment"
echo ""
echo "=============================================="
echo "✅ Ready to start fine-tuning!"
echo "=============================================="
echo ""
