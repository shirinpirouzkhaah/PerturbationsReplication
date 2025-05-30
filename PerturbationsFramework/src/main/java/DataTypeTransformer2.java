public class DataTypeTransformer2 {
    public TransformationResult transformCode(String taggedSource, String targetCode, String reviewComment) {
        String modifiedSource = replaceTypes(taggedSource);
        String modifiedTarget = replaceTypes(targetCode);
        String modifiedComment = replaceTypes(reviewComment);
        boolean sourceChanged = !modifiedSource.equals(taggedSource);
        boolean targetChanged = !modifiedTarget.equals(targetCode);
        boolean commentChanged = !modifiedComment.equals(reviewComment);
        return new TransformationResult(modifiedSource, modifiedTarget, modifiedComment, sourceChanged, targetChanged, commentChanged);
    }


    private String replaceTypes(String sourceCode) {
        String modifiedCode = sourceCode;  // Work on a copy

        modifiedCode = modifiedCode.replaceAll("\\b byte \\b", " short ");
        modifiedCode = modifiedCode.replaceAll("\\b short \\b", " int ");
        modifiedCode = modifiedCode.replaceAll("\\b int \\b", " long ");
        modifiedCode = modifiedCode.replaceAll("\\b float \\b", " double ");

        return modifiedCode;
    }



    public static class TransformationResult {
        public final String modifiedSource;
        public final String modifiedTarget;
        public final String modifiedComment;
        public final boolean sourceChanged;
        public final boolean targetChanged;
        public final boolean commentChanged;

        public TransformationResult(String modifiedSource, String modifiedTarget, String modifiedComment, boolean sourceChanged, boolean targetChanged, boolean commentChanged) {
            this.modifiedSource = modifiedSource;
            this.modifiedTarget = modifiedTarget;
            this.modifiedComment = modifiedComment;
            this.sourceChanged = sourceChanged;
            this.targetChanged = targetChanged;
            this.commentChanged = commentChanged;
        }
    }
}
