/*
 * This source file was generated by the Gradle 'init' task
 */
package net.coderextreme.ci2had;

import org.graalvm.polyglot.*;

public class App {
     public static void main(String[] args) {
         try (var context = Context.create()) {
             System.out.println(context.eval("python", "'Hello Python!'").asString());
         }
     }
}
