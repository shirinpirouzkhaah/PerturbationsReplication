import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.type.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.body.VariableDeclarator;

public class DataFlowChange extends VoidVisitorAdapter<Void> {
    private boolean modified = false;

    @Override
    public void visit(ClassOrInterfaceDeclaration n, Void arg) {
        super.visit(n, arg);
        n.getMethods().forEach(method -> {
            if (method.getBody().isPresent() && method.getBody().get().getStatements().size() == 1
                    && method.getBody().get().getStatement(0) instanceof ReturnStmt) {
                ReturnStmt returnStmt = (ReturnStmt) method.getBody().get().getStatement(0);
                if (!(returnStmt.getExpression().isPresent() && returnStmt.getExpression().get() instanceof NullLiteralExpr)) {
                    if (!method.getType().isVoidType() && !isReturningRunnable(method.getType()) && !isEffectivelyVoid(method.getType())) {
                        processReturnStatement(method, returnStmt);
                    }
                }
            }
        });
    }

    private boolean isReturningRunnable(Type type) {
        return type.toString().endsWith("Runnable"); // Check if the type ends with 'Runnable'
    }

    private boolean isEffectivelyVoid(Type type) {
        // Additional check for types like CompletableFuture<Void>
        if (type instanceof ClassOrInterfaceType) {
            ClassOrInterfaceType ciType = (ClassOrInterfaceType) type;
            if (ciType.getTypeArguments().isPresent()) {
                for (Type arg : ciType.getTypeArguments().get()) {
                    if (arg.toString().equals("Void")) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    private void processReturnStatement(MethodDeclaration method, ReturnStmt returnStmt) {
        Expression returnExpr = returnStmt.getExpression().orElse(new NullLiteralExpr());
        String varName = "returnValue";
        Type returnType = method.getType();

        BlockStmt methodBlock = new BlockStmt();
        VariableDeclarationExpr varDecl = new VariableDeclarationExpr(new VariableDeclarator(returnType, varName));
        AssignExpr assignExpr = new AssignExpr(varDecl, returnExpr, AssignExpr.Operator.ASSIGN);
        methodBlock.addStatement(assignExpr);

        NameExpr varExpr = new NameExpr(varName);
        methodBlock.addStatement(new ReturnStmt(varExpr));

        method.setBody(methodBlock);
        modified = true;
    }

    public boolean isModified() {
        return modified;
    }
}
