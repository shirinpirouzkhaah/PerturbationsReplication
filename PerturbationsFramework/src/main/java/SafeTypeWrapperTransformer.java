import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.*;

public class SafeTypeWrapperTransformer {
    private final Map<String, String> typeMapping;
    private final Map<String, String> variableTypeChanges = new HashMap<>();
    private boolean modified = false;

    public SafeTypeWrapperTransformer() {
        this.typeMapping = new HashMap<>();
        this.typeMapping.put("int", "Integer");
        this.typeMapping.put("double", "Double");
        this.typeMapping.put("boolean", "Boolean");
        this.typeMapping.put("char", "Character");
        this.typeMapping.put("float", "Float");
        this.typeMapping.put("long", "Long");
        this.typeMapping.put("short", "Short");
        this.typeMapping.put("byte", "Byte");
    }

    public TransformationResult transform(CompilationUnit cu, String sourceCode, String reviewComment, String targetCode) {
        cu.findAll(VariableDeclarator.class).forEach(var -> {
            String originalType = var.getType().toString();
            String varName = var.getNameAsString();

            if (typeMapping.containsKey(originalType) && isSafeToChange(var, cu)) {
                String newType = typeMapping.get(originalType);
                var.setType(newType);
                variableTypeChanges.put(varName, newType);
                modified = true;
            }
        });

        if (modified) {
            String modifiedSource = updateTextWithTypes(sourceCode);
            String modifiedTarget = updateTextWithTypes(targetCode);
            String modifiedComment = updateTextWithTypes(reviewComment);

            return new TransformationResult(modifiedSource, modifiedComment, modifiedTarget, true);
        }

        return new TransformationResult(sourceCode, reviewComment, targetCode, false);
    }

    private boolean isSafeToChange(VariableDeclarator var, CompilationUnit cu) {
        Node method = var.getParentNode().orElse(null);
        if (method == null) return false;

        // Check for reflection usage
        List<MethodCallExpr> methodCalls = cu.findAll(MethodCallExpr.class);
        for (MethodCallExpr call : methodCalls) {
            if (call.getNameAsString().equals("getMethod") || call.getNameAsString().equals("forName")) {
                for (Expression arg : call.getArguments()) {
                    if (arg.toString().contains(var.getNameAsString())) {
                        return false;
                    }
                }
            }
        }

        // Check for arithmetic operations and comparison operations
        List<BinaryExpr> binaryExprs = cu.findAll(BinaryExpr.class);
        for (BinaryExpr bin : binaryExprs) {
            if (bin.toString().contains(var.getNameAsString())) {
                BinaryExpr.Operator op = bin.getOperator();
                if (op == BinaryExpr.Operator.PLUS || op == BinaryExpr.Operator.MINUS ||
                        op == BinaryExpr.Operator.MULTIPLY || op == BinaryExpr.Operator.DIVIDE ||
                        op == BinaryExpr.Operator.REMAINDER ||
                        op == BinaryExpr.Operator.EQUALS || op == BinaryExpr.Operator.NOT_EQUALS ||
                        op == BinaryExpr.Operator.LESS_EQUALS || op == BinaryExpr.Operator.GREATER_EQUALS) {
                    return false;
                }
            }
        }

        // Check for method overloading resolution risk
        List<MethodDeclaration> methodDeclarations = cu.findAll(MethodDeclaration.class);
        for (MethodDeclaration methodDecl : methodDeclarations) {
            List<Parameter> params = methodDecl.getParameters();
            for (Parameter param : params) {
                if (param.getNameAsString().equals(var.getNameAsString())) {
                    return false; // Risk of ambiguous overload resolution
                }
            }
        }

        return true;
    }


    private String updateTextWithTypes(String text) {
        for (Map.Entry<String, String> entry : variableTypeChanges.entrySet()) {
            String var = entry.getKey();
            String newType = entry.getValue();
            String oldType = getKeyByValue(typeMapping, newType);

            if (oldType != null) {
                // Replace type declaration
                text = text.replaceAll("\\b" + oldType + "\\b(?=\\s+" + var + ")", newType);
                // Replace primitive mentions in comments
                text = text.replaceAll("\\b" + oldType + "\\b", newType);
            }
        }
        return text;
    }

    private String getKeyByValue(Map<String, String> map, String value) {
        for (Map.Entry<String, String> entry : map.entrySet()) {
            if (entry.getValue().equals(value)) {
                return entry.getKey();
            }
        }
        return null;
    }

    public static class TransformationResult {
        public final String modifiedSource;
        public final String modifiedComment;
        public final String modifiedTarget;
        public final boolean sourceChanged;

        public TransformationResult(String src, String comment, String tgt, boolean changed) {
            this.modifiedSource = src;
            this.modifiedComment = comment;
            this.modifiedTarget = tgt;
            this.sourceChanged = changed;
        }
    }
}
