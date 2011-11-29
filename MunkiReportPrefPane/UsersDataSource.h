//
//  UsersDataSource.h
//  MunkiReport
//
//  Created by Pelle on 2011-02-17.
//  Copyright 2011 University of Gothenburg. All rights reserved.
//

#import <Cocoa/Cocoa.h>


@interface UsernameFormatter : NSFormatter @end


@interface UsersDataSource : NSObject <NSTableViewDelegate, NSTableViewDataSource> {
    /*
     users contains a NSMutabaleArray of NSMutableDictionary, where each entry has
     the keys username, realname, and password. After updateUsersWithGroups, all
     users in the viewers group will have hasView set to YES, and all users in the
     admin group will have hasAdmin set to YES. The password is a 64-character hex
     string, where the first 8 characters (4 bytes) is a random salt, and the rest
     is a salted sha224 hash of the user's password.
     */
    NSMutableArray *users;
    /*
     groups contains a NSMutableDictionary where each key is a group name, and each
     value is a (possibly empty) NSMutableArray of NSString usernames.
     */
    NSMutableDictionary *groups;
}

- (id)init;

- (BOOL)loadUsersPlist:(NSString *)usersPath;
- (NSData *)serializeUsersPlist;
- (BOOL)loadGroupsIni:(NSString *)groupsPath;
- (NSData *)serializeGroupsIni;
- (void)updateUsersWithGroups;
- (NSData *)hashPassword:(NSString *)password;
- (NSMutableDictionary *)addUser;
- (void)removeUserAtIndex:(NSInteger)index;

// NSTableViewDataSource
- (id)tableView:(NSTableView *)aTableView
objectValueForTableColumn:(NSTableColumn *)aTableColumn
            row:(NSInteger)rowIndex;
- (NSInteger)numberOfRowsInTableView:(NSTableView *)aTableView;

// NSTableViewDelegate

@end
